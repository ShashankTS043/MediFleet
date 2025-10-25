import { Code, BookOpen, Zap, Database } from "lucide-react";
import { useState } from "react";

export default function APIDocs() {
  const [copiedEndpoint, setCopiedEndpoint] = useState(null);

  const copyToClipboard = (code, id) => {
    navigator.clipboard.writeText(code);
    setCopiedEndpoint(id);
    setTimeout(() => setCopiedEndpoint(null), 2000);
  };

  const endpoints = [
    {
      method: "GET",
      path: "/api/tasks",
      description: "Get all tasks",
      curl: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/tasks"`,
      response: `[
  {
    "id": "abc123",
    "destination": "ICU",
    "priority": "high",
    "status": "completed",
    "robot_id": "robot_01",
    "robot_name": "MediBot-A1",
    "created_at": "2025-01-25T10:30:00Z",
    "completed_at": "2025-01-25T10:35:00Z"
  }
]`
    },
    {
      method: "POST",
      path: "/api/tasks",
      description: "Create a new task",
      curl: `curl -X POST "${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/tasks" \\
  -H "Content-Type: application/json" \\
  -d '{
    "destination": "ICU",
    "priority": "high"
  }'`,
      response: `{
  "id": "abc123",
  "destination": "ICU",
  "priority": "high",
  "status": "pending",
  "created_at": "2025-01-25T10:30:00Z"
}`
    },
    {
      method: "GET",
      path: "/api/robots",
      description: "Get all robots",
      curl: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/robots"`,
      response: `[
  {
    "id": "robot_01",
    "name": "MediBot-A1",
    "status": "idle",
    "location": "ENTRANCE",
    "battery": 95,
    "tasks_completed_today": 0,
    "total_tasks": 156,
    "avg_completion_time": 4.5
  }
]`
    },
    {
      method: "PATCH",
      path: "/api/robots/{robot_id}",
      description: "Update robot status/location",
      curl: `curl -X PATCH "${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/robots/robot_01" \\
  -H "Content-Type: application/json" \\
  -d '{
    "location": "ICU",
    "status": "busy"
  }'`,
      response: `{
  "message": "Robot updated successfully"
}`
    },
    {
      method: "POST",
      path: "/api/robots/reset-all",
      description: "Reset all robots to ENTRANCE",
      curl: `curl -X POST "${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/robots/reset-all"`,
      response: `{
  "message": "All robots reset to ENTRANCE"
}`
    },
    {
      method: "GET",
      path: "/api/analytics/stats",
      description: "Get system analytics",
      curl: `curl -X GET "${process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}/api/analytics/stats"`,
      response: `{
  "total_tasks": 42,
  "active_robots": 3,
  "avg_completion_time": 4.2,
  "system_uptime": 99.8
}`
    }
  ];

  const getMethodColor = (method) => {
    const colors = {
      GET: "bg-green-100 text-green-700 border-green-300",
      POST: "bg-blue-100 text-blue-700 border-blue-300",
      PATCH: "bg-yellow-100 text-yellow-700 border-yellow-300",
      DELETE: "bg-red-100 text-red-700 border-red-300"
    };
    return colors[method] || "bg-slate-100 text-slate-700 border-slate-300";
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl mb-4">
            <BookOpen className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-4xl font-bold text-slate-800 mb-4">API Documentation</h1>
          <p className="text-base text-slate-600 max-w-2xl mx-auto">
            Complete REST API reference for MediFleet hospital robot coordination system
          </p>
        </div>

        {/* Base URL */}
        <div className="glass rounded-3xl p-8 mb-8 card-hover">
          <div className="flex items-center space-x-3 mb-4">
            <Zap className="w-6 h-6 text-cyan-600" />
            <h2 className="text-xl font-bold text-slate-800">Base URL</h2>
          </div>
          <code className="block bg-slate-800 text-cyan-400 p-4 rounded-lg text-lg font-mono">
            {process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'}
          </code>
          <p className="text-sm text-slate-600 mt-4">
            All API endpoints are prefixed with <code className="bg-slate-200 px-2 py-1 rounded">/api</code>
          </p>
        </div>

        {/* Authentication Info */}
        <div className="glass rounded-2xl p-6 mb-8 bg-cyan-50 border-2 border-cyan-200">
          <h3 className="font-semibold text-slate-800 mb-2">🔓 Authentication</h3>
          <p className="text-slate-700 text-sm">
            Currently, the API is open for demo purposes. In production, implement JWT or API key authentication.
          </p>
        </div>

        {/* Endpoints */}
        <div className="space-y-6">
          {endpoints.map((endpoint, index) => (
            <div key={index} className="glass rounded-2xl p-6 card-hover">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className={`px-3 py-1 rounded-lg text-sm font-bold border-2 ${getMethodColor(endpoint.method)}`}>
                    {endpoint.method}
                  </span>
                  <code className="text-lg font-mono text-slate-800">{endpoint.path}</code>
                </div>
              </div>
              <p className="text-slate-600 mb-4">{endpoint.description}</p>
              
              {/* cURL Example */}
              <div className="mb-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-sm font-semibold text-slate-700">cURL Example:</h4>
                  <button
                    onClick={() => copyToClipboard(endpoint.curl, `curl-${index}`)}
                    className="text-xs flex items-center space-x-1 text-cyan-600 hover:text-cyan-700"
                  >
                    <Code className="w-3 h-3" />
                    <span>{copiedEndpoint === `curl-${index}` ? 'Copied!' : 'Copy'}</span>
                  </button>
                </div>
                <pre className="bg-slate-900 text-cyan-400 p-4 rounded-lg overflow-x-auto text-xs">
                  {endpoint.curl}
                </pre>
              </div>
              
              {/* Response Example */}
              <div>
                <h4 className="text-sm font-semibold text-slate-700 mb-2">Response:</h4>
                <pre className="bg-slate-50 text-slate-700 p-4 rounded-lg overflow-x-auto text-xs border-2 border-slate-200">
                  {endpoint.response}
                </pre>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="mt-12 glass rounded-2xl p-6 text-center">
          <h3 className="font-semibold text-slate-800 mb-2">Need More Information?</h3>
          <p className="text-slate-600 mb-4">
            Check out our MQTT integration guide for hardware communication
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <a href="/mqtt-docs" className="btn-primary inline-block">
              MQTT Documentation
            </a>
            <a href="/about" className="px-6 py-3 rounded-full border-2 border-cyan-500 text-cyan-700 font-semibold hover:bg-cyan-50 transition-colors inline-block">
              About MediFleet
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}