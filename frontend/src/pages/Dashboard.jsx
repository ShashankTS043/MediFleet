import { useState, useEffect } from "react";
import axios from "axios";
import { RefreshCw, Clock, MapPin, Bot, Play, Zap } from "lucide-react";
import FloorMap from "@/components/FloorMap";
import ActivityLog from "@/components/ActivityLog";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [robots, setRobots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activityLogs, setActivityLogs] = useState([]);
  const [simulatingRobots, setSimulatingRobots] = useState(new Set());
  const [movingRobots, setMovingRobots] = useState([]);
  
  const fetchData = async () => {
    try {
      const [tasksRes, robotsRes] = await Promise.all([
        axios.get(`${API}/tasks`),
        axios.get(`${API}/robots`)
      ]);
      setTasks(tasksRes.data);
      setRobots(robotsRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);
  
  const addLog = (message) => {
    const time = new Date().toLocaleTimeString("en-US", { 
      hour: "2-digit", 
      minute: "2-digit", 
      second: "2-digit" 
    });
    setActivityLogs(prev => [...prev, { time, message }]);
  };
  
  const playArrivalSound = () => {
    // Optional: Play a subtle arrival sound
    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800;
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.3);
    } catch (error) {
      // Silently fail if audio not supported
    }
  };
  
  const simulateMovement = async (robot, task) => {
    if (simulatingRobots.has(robot.id)) return;
    
    setSimulatingRobots(prev => new Set(prev).add(robot.id));
    addLog(`🤖 ${robot.name} starting movement to ${task.destination}`);
    
    try {
      // Update task to moving
      await axios.patch(`${API}/tasks/${task.id}`, { status: "moving" });
      addLog(`📍 ${robot.name} moving to ${task.destination}`);
      
      // Add to moving robots for animation
      setMovingRobots(prev => [
        ...prev,
        {
          robotId: robot.id,
          from: robot.location,
          to: task.destination,
          isMoving: true
        }
      ]);
      
      // Wait 3 seconds for movement animation
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Remove from moving robots
      setMovingRobots(prev => prev.filter(mr => mr.robotId !== robot.id));
      
      // Update robot location
      await axios.patch(`${API}/robots/${robot.id}`, { 
        location: task.destination,
        status: "idle"
      });
      
      // Complete task
      await axios.patch(`${API}/tasks/${task.id}`, { 
        status: "completed",
        completed_at: new Date().toISOString()
      });
      
      // Play arrival sound
      playArrivalSound();
      
      addLog(`✅ ${robot.name} arrived at ${task.destination}`);
      addLog(`🎉 Task #${task.id.substring(0, 8)} completed`);
      
      toast.success(`${robot.name} completed task!`);
      
      // Refresh data
      await fetchData();
    } catch (error) {
      console.error("Error simulating movement:", error);
      toast.error("Failed to simulate movement");
      setMovingRobots(prev => prev.filter(mr => mr.robotId !== robot.id));
    } finally {
      setSimulatingRobots(prev => {
        const newSet = new Set(prev);
        newSet.delete(robot.id);
        return newSet;
      });
    }
  };
  
  const quickDemoMode = async () => {
    try {
      addLog("🚀 Quick Demo Mode initiated");
      toast.info("Starting Quick Demo Mode...");
      
      // Create 3 tasks
      const destinations = ["ICU", "ROOM_101", "EMERGENCY"];
      const priorities = ["high", "medium", "urgent"];
      
      addLog("📋 Creating 3 tasks...");
      const createdTasks = [];
      
      for (let i = 0; i < 3; i++) {
        const response = await axios.post(`${API}/tasks`, {
          destination: destinations[i],
          priority: priorities[i]
        });
        createdTasks.push(response.data);
        addLog(`✓ Task created: ${destinations[i]} (${priorities[i]} priority)`);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      // Wait for bidding to complete
      addLog("⚡ Robot bidding in progress...");
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Refresh to get assigned tasks
      await fetchData();
      
      addLog("🎯 Tasks assigned to robots");
      
      // Wait a bit then simulate all movements
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      addLog("🏃 Simulating multi-robot coordination...");
      
      // Get updated tasks
      const tasksRes = await axios.get(`${API}/tasks`);
      const assignedTasks = tasksRes.data.filter(t => 
        t.status === "assigned" || t.status === "moving"
      );
      
      // Simulate all robot movements in parallel
      const robotsRes = await axios.get(`${API}/robots`);
      const allRobots = robotsRes.data;
      
      const movements = assignedTasks.map(task => {
        const robot = allRobots.find(r => r.id === task.robot_id);
        if (robot) {
          return simulateMovement(robot, task);
        }
        return Promise.resolve();
      });
      
      await Promise.all(movements);
      
      addLog("✨ Quick Demo Mode completed successfully");
      toast.success("Demo completed! All robots coordinated.");
      
    } catch (error) {
      console.error("Error in quick demo mode:", error);
      toast.error("Demo mode failed");
      addLog("❌ Demo mode encountered an error");
    }
  };
  
  const formatTime = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  };
  
  const getAssignedTask = (robotId) => {
    return tasks.find(t => t.robot_id === robotId && (t.status === "assigned" || t.status === "moving"));
  };
  
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-800 mb-2" data-testid="dashboard-title">
              Task Dashboard
            </h1>
            <p className="text-base text-slate-600">
              Real-time tracking of all robot tasks
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={quickDemoMode}
              className="flex items-center space-x-2 px-5 py-2.5 bg-gradient-to-r from-purple-500 to-pink-600 rounded-full text-white font-semibold hover:shadow-lg transition-all"
              data-testid="quick-demo-btn"
            >
              <Zap className="w-4 h-4" />
              <span>Quick Demo</span>
            </button>
            <button
              onClick={fetchData}
              className="flex items-center space-x-2 px-5 py-2.5 bg-white rounded-full border-2 border-cyan-200 text-cyan-700 font-semibold hover:bg-cyan-50 transition-colors"
              data-testid="dashboard-refresh-btn"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh</span>
            </button>
          </div>
        </div>
        
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
            <p className="mt-4 text-slate-600">Loading dashboard...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Floor Map - Centerpiece */}
            <FloorMap robots={robots} movingRobots={movingRobots} />
            
            {/* Robot Status Cards */}
            <div>
              <h2 className="text-2xl font-bold text-slate-800 mb-4">Robot Fleet Status</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {robots.map(robot => {
                  const assignedTask = getAssignedTask(robot.id);
                  const isSimulating = simulatingRobots.has(robot.id);
                  
                  return (
                    <div
                      key={robot.id}
                      className="glass rounded-xl p-4 card-hover"
                      data-testid={`robot-card-${robot.id}`}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="font-bold text-slate-800">{robot.name}</h3>
                          <span className={`status-badge status-${robot.status} text-xs`}>
                            {robot.status}
                          </span>
                        </div>
                        <div className="text-2xl">🤖</div>
                      </div>
                      
                      <div className="text-xs text-slate-600 mb-3">
                        <div>📍 {robot.location}</div>
                        <div>🔋 {robot.battery}%</div>
                      </div>
                      
                      {assignedTask && (
                        <div className="mb-3 p-2 bg-cyan-50 rounded text-xs">
                          <div className="font-semibold text-slate-700">Task: {assignedTask.destination}</div>
                          <div className="text-slate-500">{assignedTask.priority} priority</div>
                        </div>
                      )}
                      
                      {assignedTask && (
                        <button
                          onClick={() => simulateMovement(robot, assignedTask)}
                          disabled={isSimulating || assignedTask.status === "moving"}
                          className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-lg text-sm font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                          data-testid={`simulate-btn-${robot.id}`}
                        >
                          <Play className="w-3 h-3" />
                          <span>{isSimulating ? "Simulating..." : "Simulate Movement"}</span>
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Activity Log */}
            <ActivityLog logs={activityLogs} />
            
            {/* Tasks Section */}
            <div>
              <h2 className="text-2xl font-bold text-slate-800 mb-4">Active Tasks</h2>
              {tasks.length === 0 ? (
                <div className="glass rounded-3xl p-12 text-center" data-testid="dashboard-no-tasks">
                  <div className="text-6xl mb-4">📋</div>
                  <h3 className="text-xl font-semibold text-slate-800 mb-2">No Tasks Yet</h3>
                  <p className="text-slate-600">Create your first task to get started</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  {tasks.map((task) => (
                    <div
                      key={task.id}
                      className="glass rounded-2xl p-6 card-hover"
                      data-testid={`task-${task.id}`}
                      style={{
                        transition: "all 0.5s ease-out"
                      }}
                    >
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-3">
                            <span 
                              className={`status-badge status-${task.status}`} 
                              data-testid={`task-status-${task.status}`}
                              style={{ transition: "all 0.3s ease-out" }}
                            >
                              {task.status}
                            </span>
                            <span className={`status-badge priority-${task.priority}`} data-testid={`task-priority-${task.priority}`}>
                              {task.priority}
                            </span>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2 text-slate-700">
                              <MapPin className="w-4 h-4 text-cyan-600" />
                              <span className="font-semibold">Destination:</span>
                              <span>{task.destination}</span>
                            </div>
                            
                            {task.robot_name && (
                              <div className="flex items-center space-x-2 text-slate-700">
                                <Bot className="w-4 h-4 text-cyan-600" />
                                <span className="font-semibold">Robot:</span>
                                <span>{task.robot_name}</span>
                              </div>
                            )}
                            
                            <div className="flex items-center space-x-2 text-slate-600 text-sm">
                              <Clock className="w-4 h-4" />
                              <span>Created: {formatTime(task.created_at)}</span>
                              {task.completed_at && (
                                <span className="ml-4">Completed: {formatTime(task.completed_at)}</span>
                              )}
                            </div>
                          </div>
                        </div>
                        
                        {/* Status Progress */}
                        <div className="flex items-center space-x-2">
                          {["pending", "bidding", "assigned", "moving", "completed"].map((status, index) => {
                            const statusIndex = ["pending", "bidding", "assigned", "moving", "completed"].indexOf(task.status);
                            const isActive = index <= statusIndex;
                            return (
                              <div
                                key={status}
                                className={`w-3 h-3 rounded-full transition-all duration-500 ${
                                  isActive ? "bg-gradient-to-r from-cyan-500 to-blue-600 shadow-lg" : "bg-slate-200"
                                }`}
                                title={status}
                              ></div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}