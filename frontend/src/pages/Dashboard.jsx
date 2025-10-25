import { useState, useEffect } from "react";
import axios from "axios";
import { RefreshCw, Clock, MapPin, Bot } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  
  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchTasks();
    
    // Auto-refresh every 3 seconds
    const interval = setInterval(fetchTasks, 3000);
    return () => clearInterval(interval);
  }, []);
  
  const formatTime = (dateString) => {
    if (!dateString) return "N/A";
    const date = new Date(dateString);
    return date.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
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
          <button
            onClick={fetchTasks}
            className="flex items-center space-x-2 px-5 py-2.5 bg-white rounded-full border-2 border-cyan-200 text-cyan-700 font-semibold hover:bg-cyan-50 transition-colors"
            data-testid="dashboard-refresh-btn"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Refresh</span>
          </button>
        </div>
        
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
            <p className="mt-4 text-slate-600">Loading tasks...</p>
          </div>
        ) : tasks.length === 0 ? (
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
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-3">
                      <span className={`status-badge status-${task.status}`} data-testid={`task-status-${task.status}`}>
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
                          className={`w-3 h-3 rounded-full transition-all ${
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
  );
}