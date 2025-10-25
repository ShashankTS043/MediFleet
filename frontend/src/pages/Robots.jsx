import { useState, useEffect } from "react";
import axios from "axios";
import { Battery, MapPin, TrendingUp, Award } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Robots() {
  const [robots, setRobots] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchRobots = async () => {
      try {
        const response = await axios.get(`${API}/robots`);
        setRobots(response.data);
      } catch (error) {
        console.error("Error fetching robots:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchRobots();
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchRobots, 5000);
    return () => clearInterval(interval);
  }, []);
  
  const getBatteryColor = (battery) => {
    if (battery >= 80) return "from-green-500 to-emerald-500";
    if (battery >= 50) return "from-yellow-500 to-orange-500";
    if (battery >= 20) return "from-orange-500 to-red-500";
    return "from-red-500 to-pink-500";
  };
  
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-800 mb-3" data-testid="robots-title">
            Robot Fleet
          </h1>
          <p className="text-base text-slate-600">
            Monitor all robots with detailed metrics and real-time status
          </p>
        </div>
        
        {loading ? (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
            <p className="mt-4 text-slate-600">Loading robots...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
            {robots.map((robot) => (
              <div
                key={robot.id}
                className="glass rounded-2xl p-6 card-hover"
                data-testid={`robot-${robot.id}`}
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-xl font-bold text-slate-800 mb-2">{robot.name}</h3>
                    <span className={`status-badge status-${robot.status}`} data-testid={`robot-status-${robot.status}`}>
                      {robot.status}
                    </span>
                  </div>
                  <div className="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center text-2xl">
                    🤖
                  </div>
                </div>
                
                {/* Battery */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Battery className="w-4 h-4 text-slate-600" />
                      <span className="text-sm font-semibold text-slate-700">Battery</span>
                    </div>
                    <span className="text-sm font-bold text-slate-800">{robot.battery}%</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${getBatteryColor(robot.battery)} transition-all duration-500`}
                      style={{ width: `${robot.battery}%` }}
                    ></div>
                  </div>
                </div>
                
                {/* Location */}
                <div className="flex items-center space-x-2 mb-6 text-slate-700">
                  <MapPin className="w-4 h-4 text-cyan-600" />
                  <span className="text-sm font-semibold">Location:</span>
                  <span className="text-sm">{robot.location}</span>
                </div>
                
                {/* Metrics */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-slate-800">{robot.tasks_completed_today}</div>
                    <div className="text-xs text-slate-600 mt-1">Today</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-slate-800">{robot.total_tasks}</div>
                    <div className="text-xs text-slate-600 mt-1">Total</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-slate-800">{robot.avg_completion_time}<span className="text-base">m</span></div>
                    <div className="text-xs text-slate-600 mt-1">Avg Time</div>
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