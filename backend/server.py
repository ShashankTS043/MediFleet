from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import random
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Robot(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str  # idle, busy, charging, maintenance
    location: str
    battery: int
    tasks_completed_today: int = 0
    total_tasks: int = 0
    avg_completion_time: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RobotCreate(BaseModel):
    name: str
    location: str
    battery: int = 100

class RobotUpdate(BaseModel):
    status: Optional[str] = None
    location: Optional[str] = None
    battery: Optional[int] = None

class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    destination: str
    priority: str  # low, medium, high, urgent
    status: str  # pending, bidding, assigned, moving, completed
    robot_id: Optional[str] = None
    robot_name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskCreate(BaseModel):
    destination: str
    priority: str

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[str] = None

class AnalyticsStats(BaseModel):
    total_tasks: int
    active_robots: int
    avg_completion_time: float
    system_uptime: float

# Initialize some robots on startup
async def initialize_robots():
    count = await db.robots.count_documents({})
    if count == 0:
        robots = [
            {"id": str(uuid.uuid4()), "name": "MediBot-A1", "status": "idle", "location": "ENTRANCE", 
             "battery": 95, "tasks_completed_today": 0, "total_tasks": 156, "avg_completion_time": 4.5,
             "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "MediBot-B2", "status": "idle", "location": "ENTRANCE", 
             "battery": 85, "tasks_completed_today": 0, "total_tasks": 203, "avg_completion_time": 5.2,
             "created_at": datetime.now(timezone.utc).isoformat()},
            {"id": str(uuid.uuid4()), "name": "MediBot-C3", "status": "idle", "location": "ENTRANCE", 
             "battery": 100, "tasks_completed_today": 0, "total_tasks": 189, "avg_completion_time": 3.8,
             "created_at": datetime.now(timezone.utc).isoformat()},
        ]
        await db.robots.insert_many(robots)
    else:
        # Delete any extra robots beyond 3
        all_robots = await db.robots.find({}, {"_id": 0, "id": 1}).sort("created_at", 1).to_list(100)
        if len(all_robots) > 3:
            robots_to_delete = [r["id"] for r in all_robots[3:]]
            await db.robots.delete_many({"id": {"$in": robots_to_delete}})
        
        # Reset remaining robots to ENTRANCE on startup
        await db.robots.update_many(
            {},
            {"$set": {
                "location": "ENTRANCE",
                "status": "idle",
                "tasks_completed_today": 0
            }}
        )

@app.on_event("startup")
async def startup_event():
    await initialize_robots()

# Routes
@api_router.get("/")
async def root():
    return {"message": "MediFleet API"}

# Task routes
@api_router.post("/tasks", response_model=Task)
async def create_task(task_input: TaskCreate):
    task_dict = task_input.model_dump()
    task_obj = Task(**task_dict, status="pending")
    
    doc = task_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.tasks.insert_one(doc)
    
    # Start bidding process in background
    asyncio.create_task(process_bidding(task_obj.id))
    
    return task_obj

@api_router.get("/tasks", response_model=List[Task])
async def get_tasks():
    tasks = await db.tasks.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    for task in tasks:
        if isinstance(task.get('created_at'), str):
            task['created_at'] = datetime.fromisoformat(task['created_at'])
        if isinstance(task.get('assigned_at'), str):
            task['assigned_at'] = datetime.fromisoformat(task['assigned_at'])
        if isinstance(task.get('completed_at'), str):
            task['completed_at'] = datetime.fromisoformat(task['completed_at'])
    
    return tasks

@api_router.get("/tasks/{task_id}", response_model=Task)
async def get_task(task_id: str):
    task = await db.tasks.find_one({"id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if isinstance(task.get('created_at'), str):
        task['created_at'] = datetime.fromisoformat(task['created_at'])
    if isinstance(task.get('assigned_at'), str):
        task['assigned_at'] = datetime.fromisoformat(task['assigned_at'])
    if isinstance(task.get('completed_at'), str):
        task['completed_at'] = datetime.fromisoformat(task['completed_at'])
    
    return task

@api_router.patch("/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate):
    update_data = {k: v for k, v in task_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.tasks.update_one(
        {"id": task_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"message": "Task updated successfully"}

# Robot routes
@api_router.get("/robots", response_model=List[Robot])
async def get_robots():
    robots = await db.robots.find({}, {"_id": 0}).to_list(1000)
    
    for robot in robots:
        if isinstance(robot.get('created_at'), str):
            robot['created_at'] = datetime.fromisoformat(robot['created_at'])
    
    return robots

@api_router.get("/robots/{robot_id}", response_model=Robot)
async def get_robot(robot_id: str):
    robot = await db.robots.find_one({"id": robot_id}, {"_id": 0})
    if not robot:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    if isinstance(robot.get('created_at'), str):
        robot['created_at'] = datetime.fromisoformat(robot['created_at'])
    
    return robot

@api_router.patch("/robots/{robot_id}")
async def update_robot(robot_id: str, robot_update: RobotUpdate):
    update_data = {k: v for k, v in robot_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.robots.update_one(
        {"id": robot_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Robot not found")
    
    return {"message": "Robot updated successfully"}

@api_router.post("/robots/reset-all")
async def reset_all_robots():
    """Reset all robots to ENTRANCE location"""
    await db.robots.update_many(
        {},
        {"$set": {
            "location": "ENTRANCE",
            "status": "idle",
            "tasks_completed_today": 0
        }}
    )
    return {"message": "All robots reset to ENTRANCE"}

# Analytics routes
@api_router.get("/analytics/stats", response_model=AnalyticsStats)
async def get_analytics_stats():
    total_tasks = await db.tasks.count_documents({})
    active_robots = await db.robots.count_documents({"status": {"$in": ["idle", "busy"]}})
    
    # Calculate average completion time
    completed_tasks = await db.tasks.find({"status": "completed"}).to_list(1000)
    if completed_tasks:
        completion_times = []
        for task in completed_tasks:
            if task.get('completed_at') and task.get('created_at'):
                completed = datetime.fromisoformat(task['completed_at']) if isinstance(task['completed_at'], str) else task['completed_at']
                created = datetime.fromisoformat(task['created_at']) if isinstance(task['created_at'], str) else task['created_at']
                completion_times.append((completed - created).total_seconds() / 60)
        avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    else:
        avg_completion_time = 0
    
    return {
        "total_tasks": total_tasks,
        "active_robots": active_robots,
        "avg_completion_time": round(avg_completion_time, 1),
        "system_uptime": 99.8
    }

@api_router.get("/analytics/tasks-over-time")
async def get_tasks_over_time():
    # Return simulated data for last 7 days
    return [
        {"date": "Mon", "tasks": 45},
        {"date": "Tue", "tasks": 52},
        {"date": "Wed", "tasks": 38},
        {"date": "Thu", "tasks": 61},
        {"date": "Fri", "tasks": 48},
        {"date": "Sat", "tasks": 35},
        {"date": "Sun", "tasks": 42}
    ]

@api_router.get("/analytics/destination-popularity")
async def get_destination_popularity():
    pipeline = [
        {"$group": {"_id": "$destination", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    results = await db.tasks.aggregate(pipeline).to_list(10)
    return [{"destination": r["_id"], "count": r["count"]} for r in results]

@api_router.get("/analytics/priority-distribution")
async def get_priority_distribution():
    pipeline = [
        {"$group": {"_id": "$priority", "count": {"$sum": 1}}}
    ]
    results = await db.tasks.aggregate(pipeline).to_list(10)
    return [{"priority": r["_id"], "count": r["count"]} for r in results]

@api_router.get("/analytics/robot-performance")
async def get_robot_performance():
    robots = await db.robots.find({}, {"_id": 0}).to_list(10)
    return [{"name": r["name"], "tasks_completed": r["total_tasks"], "avg_time": r["avg_completion_time"]} for r in robots]

# Background task processing
async def process_bidding(task_id: str):
    # Simulate bidding process
    await asyncio.sleep(2)
    
    # Update task to bidding
    await db.tasks.update_one(
        {"id": task_id},
        {"$set": {"status": "bidding"}}
    )
    
    await asyncio.sleep(3)
    
    # Find available robot
    available_robots = await db.robots.find({"status": "idle"}, {"_id": 0}).to_list(10)
    
    if available_robots:
        # Select robot with highest battery
        selected_robot = max(available_robots, key=lambda r: r["battery"])
        
        # Assign task
        await db.tasks.update_one(
            {"id": task_id},
            {"$set": {
                "status": "assigned",
                "robot_id": selected_robot["id"],
                "robot_name": selected_robot["name"],
                "assigned_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        # Update robot status
        await db.robots.update_one(
            {"id": selected_robot["id"]},
            {"$set": {"status": "busy"}}
        )

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()