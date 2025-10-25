import { useState, useEffect } from "react";
import { Tooltip } from "@/components/ui/tooltip";

const waypoints = {
  "Entrance": { x: 50, y: 10, color: "#ffffff", border: "#94a3b8", label: "ENTRANCE" },
  "Pharmacy": { x: 50, y: 30, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "ICU": { x: 20, y: 55, color: "#ef4444", border: "#dc2626", label: "ICU" },
  "Emergency Room": { x: 50, y: 55, color: "#fbbf24", border: "#f59e0b", label: "EMERGENCY" },
  "Room 101": { x: 80, y: 55, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "Storage": { x: 50, y: 80, color: "#a855f7", border: "#9333ea", label: "STORAGE" },
  "Charging Station": { x: 50, y: 80, color: "#a855f7", border: "#9333ea", label: "STORAGE" },
  "Surgery Wing": { x: 50, y: 30, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "Laboratory": { x: 50, y: 30, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "Radiology": { x: 20, y: 55, color: "#ef4444", border: "#dc2626", label: "ICU" },
  "Pediatrics": { x: 80, y: 55, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "Cardiology": { x: 50, y: 55, color: "#fbbf24", border: "#f59e0b", label: "EMERGENCY" },
  "Oncology": { x: 80, y: 55, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "Neurology": { x: 20, y: 55, color: "#ef4444", border: "#dc2626", label: "ICU" }
};

const connections = [
  // Direct paths from Entrance
  ["Entrance", "ICU"],
  ["Entrance", "Pharmacy"],
  ["Entrance", "Room 101"],
  // Paths from Pharmacy
  ["Pharmacy", "ICU"],
  ["Pharmacy", "Emergency Room"],
  ["Pharmacy", "Room 101"],
  // Path to Storage
  ["Emergency Room", "Storage"]
];

export default function FloorMap({ robots }) {
  const [hoveredWaypoint, setHoveredWaypoint] = useState(null);
  const [robotPositions, setRobotPositions] = useState({});

  // Update robot positions with animation
  useEffect(() => {
    const newPositions = {};
    robots.forEach(robot => {
      const location = robot.location;
      const waypoint = waypoints[location] || waypoints["Pharmacy"];
      newPositions[robot.id] = {
        x: waypoint.x,
        y: waypoint.y,
        name: robot.name,
        status: robot.status,
        battery: robot.battery
      };
    });
    setRobotPositions(newPositions);
  }, [robots]);

  const getWaypointInfo = (location) => {
    const robotsHere = robots.filter(r => r.location === location);
    return {
      location,
      robotCount: robotsHere.length,
      robots: robotsHere
    };
  };

  return (
    <div className="glass rounded-3xl p-8 card-hover" data-testid="floor-map">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-slate-800 mb-2">Hospital Floor Map</h2>
        <p className="text-sm text-slate-600">Real-time robot location tracking</p>
      </div>

      <div className="relative w-full" style={{ paddingBottom: "100%" }}>
        <svg
          className="absolute inset-0 w-full h-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style={{ stopColor: "#06b6d4", stopOpacity: 0.8 }} />
              <stop offset="100%" style={{ stopColor: "#0ea5e9", stopOpacity: 0.4 }} />
            </linearGradient>
          </defs>

          {/* Connection Lines */}
          {connections.map(([start, end], index) => {
            const startPoint = waypoints[start];
            const endPoint = waypoints[end];
            return (
              <line
                key={index}
                x1={startPoint.x}
                y1={startPoint.y}
                x2={endPoint.x}
                y2={endPoint.y}
                stroke="url(#lineGradient)"
                strokeWidth="0.5"
                strokeDasharray="2,2"
                opacity="0.6"
              />
            );
          })}

          {/* Waypoints */}
          {Object.entries(waypoints).map(([location, point]) => {
            if (["Charging Station", "Surgery Wing", "Laboratory", "Radiology", "Pediatrics", "Cardiology", "Oncology", "Neurology"].includes(location)) {
              return null; // Skip duplicates
            }
            
            const info = getWaypointInfo(location);
            const isHovered = hoveredWaypoint === location;

            return (
              <g key={location}>
                {/* Outer glow when hovered */}
                {isHovered && (
                  <circle
                    cx={point.x}
                    cy={point.y}
                    r="6"
                    fill={point.color}
                    opacity="0.3"
                    filter="url(#glow)"
                  />
                )}

                {/* Main waypoint circle */}
                <circle
                  cx={point.x}
                  cy={point.y}
                  r="4"
                  fill={point.color}
                  stroke={point.border}
                  strokeWidth="0.5"
                  className="cursor-pointer transition-all duration-300"
                  onMouseEnter={() => setHoveredWaypoint(location)}
                  onMouseLeave={() => setHoveredWaypoint(null)}
                  style={{
                    filter: isHovered ? "drop-shadow(0 0 8px rgba(6, 182, 212, 0.8))" : "none",
                    transform: isHovered ? "scale(1.2)" : "scale(1)",
                    transformOrigin: `${point.x}% ${point.y}%`
                  }}
                />

                {/* Label */}
                <text
                  x={point.x}
                  y={point.y + 7}
                  textAnchor="middle"
                  fontSize="2.5"
                  fontWeight="600"
                  fill="#1e293b"
                  className="pointer-events-none select-none"
                >
                  {point.label}
                </text>

                {/* Robot count badge */}
                {info.robotCount > 0 && (
                  <g>
                    <circle
                      cx={point.x + 3}
                      cy={point.y - 3}
                      r="1.5"
                      fill="#ef4444"
                      stroke="#fff"
                      strokeWidth="0.3"
                    />
                    <text
                      x={point.x + 3}
                      y={point.y - 2.2}
                      textAnchor="middle"
                      fontSize="1.5"
                      fontWeight="bold"
                      fill="#fff"
                      className="pointer-events-none select-none"
                    >
                      {info.robotCount}
                    </text>
                  </g>
                )}
              </g>
            );
          })}

          {/* Robots */}
          {Object.entries(robotPositions).map(([robotId, pos]) => (
            <g key={robotId} className="robot-icon">
              {/* Robot shadow */}
              <ellipse
                cx={pos.x}
                cy={pos.y + 1.5}
                rx="1.5"
                ry="0.5"
                fill="#000"
                opacity="0.2"
                style={{
                  transition: "all 1s cubic-bezier(0.4, 0, 0.2, 1)"
                }}
              />
              
              {/* Robot emoji */}
              <text
                x={pos.x}
                y={pos.y}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize="4"
                className="cursor-pointer"
                style={{
                  transition: "all 1s cubic-bezier(0.4, 0, 0.2, 1)",
                  filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.3))"
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "scale(1.3)";
                  e.currentTarget.style.transformOrigin = "center";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "scale(1)";
                }}
              >
                🤖
              </text>
              
              {/* Robot name on hover */}
              <text
                x={pos.x}
                y={pos.y - 4}
                textAnchor="middle"
                fontSize="1.8"
                fontWeight="600"
                fill="#1e293b"
                className="opacity-0 hover:opacity-100 transition-opacity pointer-events-none"
                style={{
                  textShadow: "0 0 4px rgba(255,255,255,0.9)"
                }}
              >
                {pos.name}
              </text>
            </g>
          ))}
        </svg>

        {/* Tooltip for hovered waypoint */}
        {hoveredWaypoint && (
          <div
            className="absolute bg-slate-800 text-white px-4 py-3 rounded-xl shadow-2xl z-50 pointer-events-none"
            style={{
              left: `${waypoints[hoveredWaypoint].x}%`,
              top: `${waypoints[hoveredWaypoint].y}%`,
              transform: "translate(-50%, calc(-100% - 20px))",
              animation: "fadeIn 0.2s ease-out"
            }}
          >
            <div className="text-sm font-bold mb-1">{hoveredWaypoint}</div>
            <div className="text-xs text-slate-300">
              {getWaypointInfo(hoveredWaypoint).robotCount > 0 ? (
                <div>
                  <div className="mb-1">🤖 {getWaypointInfo(hoveredWaypoint).robotCount} robot(s) here</div>
                  {getWaypointInfo(hoveredWaypoint).robots.map(r => (
                    <div key={r.id} className="text-xs">
                      • {r.name} ({r.battery}%)
                    </div>
                  ))}
                </div>
              ) : (
                "No robots at this location"
              )}
            </div>
            {/* Arrow pointer */}
            <div
              className="absolute left-1/2 bottom-0 w-0 h-0"
              style={{
                transform: "translate(-50%, 100%)",
                borderLeft: "6px solid transparent",
                borderRight: "6px solid transparent",
                borderTop: "6px solid #1e293b"
              }}
            ></div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-3 gap-3">
        {[
          { label: "Entrance", color: "#ffffff", border: "#94a3b8" },
          { label: "Pharmacy", color: "#3b82f6", border: "#2563eb" },
          { label: "ICU", color: "#ef4444", border: "#dc2626" },
          { label: "Emergency", color: "#fbbf24", border: "#f59e0b" },
          { label: "Room 101", color: "#10b981", border: "#059669" },
          { label: "Storage", color: "#a855f7", border: "#9333ea" }
        ].map((item) => (
          <div key={item.label} className="flex items-center space-x-2">
            <div
              className="w-4 h-4 rounded-full"
              style={{
                backgroundColor: item.color,
                border: `2px solid ${item.border}`
              }}
            ></div>
            <span className="text-xs text-slate-600 font-medium">{item.label}</span>
          </div>
        ))}
      </div>

      <style>{`
        .robot-icon text {
          transition: transform 0.2s ease-out;
        }
      `}</style>
    </div>
  );
}