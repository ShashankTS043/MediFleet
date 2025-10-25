import { useEffect, useRef } from "react";
import { Activity } from "lucide-react";

export default function ActivityLog({ logs }) {
  const logEndRef = useRef(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="glass rounded-2xl p-6" data-testid="activity-log">
      <div className="flex items-center space-x-2 mb-4">
        <Activity className="w-5 h-5 text-cyan-600" />
        <h3 className="text-lg font-bold text-slate-800">Activity Log</h3>
      </div>
      <div className="max-h-64 overflow-y-auto space-y-2">
        {logs.length === 0 ? (
          <p className="text-sm text-slate-500 text-center py-4">No activity yet</p>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              className="text-sm text-slate-700 p-2 bg-cyan-50 rounded-lg"
              style={{
                animation: "fadeIn 0.5s ease-out"
              }}
            >
              <span className="text-xs text-slate-500 mr-2">{log.time}</span>
              {log.message}
            </div>
          ))
        )}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}