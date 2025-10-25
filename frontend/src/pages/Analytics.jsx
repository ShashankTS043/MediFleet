import { useState, useEffect } from "react";
import axios from "axios";
import { TrendingUp, Bot, Clock, Activity, Download } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [tasksOverTime, setTasksOverTime] = useState([]);
  const [destinations, setDestinations] = useState([]);
  const [robotPerformance, setRobotPerformance] = useState([]);
  const [priorities, setPriorities] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [statsRes, tasksRes, destRes, robotRes, prioRes] = await Promise.all([
          axios.get(`${API}/analytics/stats`),
          axios.get(`${API}/analytics/tasks-over-time`),
          axios.get(`${API}/analytics/destination-popularity`),
          axios.get(`${API}/analytics/robot-performance`),
          axios.get(`${API}/analytics/priority-distribution`)
        ]);
        
        setStats(statsRes.data);
        setTasksOverTime(tasksRes.data);
        setDestinations(destRes.data);
        setRobotPerformance(robotRes.data);
        setPriorities(prioRes.data);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchAnalytics();
  }, []);
  
  const exportToCSV = () => {
    const csvData = [
      ["Metric", "Value"],
      ["Total Tasks", stats?.total_tasks || 0],
      ["Active Robots", stats?.active_robots || 0],
      ["Avg Completion Time", `${stats?.avg_completion_time || 0} min`],
      ["System Uptime", `${stats?.system_uptime || 0}%`]
    ];
    
    const csv = csvData.map(row => row.join(",")).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "medifleet-analytics.csv";
    a.click();
  };
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-cyan-500 border-t-transparent"></div>
          <p className="mt-4 text-slate-600">Loading analytics...</p>
        </div>
      </div>
    );
  }
  
  const maxTasks = Math.max(...tasksOverTime.map(d => d.tasks), 1);
  const maxDest = Math.max(...destinations.map(d => d.count), 1);
  const maxRobot = Math.max(...robotPerformance.map(r => r.tasks_completed), 1);
  const totalPriorities = priorities.reduce((sum, p) => sum + p.count, 0);
  
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-800 mb-2" data-testid="analytics-title">
              Analytics Dashboard
            </h1>
            <p className="text-base text-slate-600">
              Comprehensive insights and performance metrics
            </p>
          </div>
          <button
            onClick={exportToCSV}
            className="flex items-center space-x-2 btn-primary"
            data-testid="export-csv-btn"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </button>
        </div>
        
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <div className="glass rounded-2xl p-6 card-hover" data-testid="metric-total-tasks">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-3xl font-bold text-slate-800 mb-1">{stats.total_tasks}</div>
            <div className="text-sm text-slate-600">Total Tasks</div>
          </div>
          
          <div className="glass rounded-2xl p-6 card-hover" data-testid="metric-active-robots">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-3xl font-bold text-slate-800 mb-1">{stats.active_robots}</div>
            <div className="text-sm text-slate-600">Active Robots</div>
          </div>
          
          <div className="glass rounded-2xl p-6 card-hover" data-testid="metric-avg-completion">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                <Clock className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-3xl font-bold text-slate-800 mb-1">{stats.avg_completion_time}<span className="text-lg">m</span></div>
            <div className="text-sm text-slate-600">Avg Completion Time</div>
          </div>
          
          <div className="glass rounded-2xl p-6 card-hover" data-testid="metric-uptime">
            <div className="flex items-center justify-between mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-3xl font-bold text-slate-800 mb-1">{stats.system_uptime}%</div>
            <div className="text-sm text-slate-600">System Uptime</div>
          </div>
        </div>
        
        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Tasks Over Time */}
          <div className="glass rounded-2xl p-6" data-testid="chart-tasks-over-time">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Tasks Over Time</h3>
            <div className="space-y-3">
              {tasksOverTime.map((day, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-slate-700">{day.date}</span>
                    <span className="text-sm text-slate-600">{day.tasks} tasks</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all"
                      style={{ width: `${(day.tasks / maxTasks) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Destination Popularity */}
          <div className="glass rounded-2xl p-6" data-testid="chart-destination-popularity">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Destination Popularity</h3>
            <div className="space-y-3">
              {destinations.slice(0, 5).map((dest, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-slate-700">{dest.destination}</span>
                    <span className="text-sm text-slate-600">{dest.count}</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-pink-600 transition-all"
                      style={{ width: `${(dest.count / maxDest) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Robot Performance */}
          <div className="glass rounded-2xl p-6" data-testid="chart-robot-performance">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Robot Performance</h3>
            <div className="space-y-3">
              {robotPerformance.map((robot, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-semibold text-slate-700">{robot.name}</span>
                    <span className="text-sm text-slate-600">{robot.tasks_completed} tasks</span>
                  </div>
                  <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-orange-500 to-red-600 transition-all"
                      style={{ width: `${(robot.tasks_completed / maxRobot) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {/* Priority Distribution */}
          <div className="glass rounded-2xl p-6" data-testid="chart-priority-distribution">
            <h3 className="text-lg font-bold text-slate-800 mb-6">Priority Distribution</h3>
            <div className="flex items-center justify-center h-64">
              <div className="relative w-48 h-48">
                {priorities.map((priority, index) => {
                  const percentage = (priority.count / totalPriorities) * 100;
                  const colors = {
                    low: "from-blue-500 to-cyan-500",
                    medium: "from-yellow-500 to-orange-500",
                    high: "from-orange-500 to-red-500",
                    urgent: "from-red-500 to-pink-500"
                  };
                  return (
                    <div key={index} className="mb-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold text-slate-700 capitalize">{priority.priority}</span>
                        <span className="text-sm text-slate-600">{percentage.toFixed(1)}%</span>
                      </div>
                      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full bg-gradient-to-r ${colors[priority.priority]} transition-all`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}