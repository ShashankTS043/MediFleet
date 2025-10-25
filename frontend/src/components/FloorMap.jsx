import { useState, useEffect } from "react";

const waypoints = {
  "ENTRANCE": { x: 50, y: 12, color: "#ffffff", border: "#94a3b8", label: "ROBOT PARKING", width: 24, height: 14, isParking: true },
  "ICU": { x: 20, y: 40, color: "#ef4444", border: "#dc2626", label: "ICU" },
  "PHARMACY": { x: 50, y: 40, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "ROOM_101": { x: 80, y: 40, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "EMERGENCY": { x: 50, y: 65, color: "#fbbf24", border: "#f59e0b", label: "EMERGENCY" },
  "STORAGE": { x: 50, y: 88, color: "#a855f7", border: "#9333ea", label: "STORAGE" },
  // Aliases for backward compatibility
  "Entrance": { x: 50, y: 12, color: "#ffffff", border: "#94a3b8", label: "ROBOT PARKING", width: 24, height: 14, isParking: true },
  "Pharmacy": { x: 50, y: 40, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "Room 101": { x: 80, y: 40, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "Emergency Room": { x: 50, y: 65, color: "#fbbf24", border: "#f59e0b", label: "EMERGENCY" },
  "Storage": { x: 50, y: 88, color: "#a855f7", border: "#9333ea", label: "STORAGE" },
  "Charging Station": { x: 50, y: 88, color: "#a855f7", border: "#9333ea", label: "STORAGE" },
  "Surgery Wing": { x: 50, y: 40, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "Laboratory": { x: 50, y: 40, color: "#3b82f6", border: "#2563eb", label: "PHARMACY" },
  "Radiology": { x: 20, y: 40, color: "#ef4444", border: "#dc2626", label: "ICU" },
  "Pediatrics": { x: 80, y: 40, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "Cardiology": { x: 50, y: 65, color: "#fbbf24", border: "#f59e0b", label: "EMERGENCY" },
  "Oncology": { x: 80, y: 40, color: "#10b981", border: "#059669", label: "ROOM 101" },
  "Neurology": { x: 20, y: 40, color: "#ef4444", border: "#dc2626", label: "ICU" }
};

const connections = [
  // Entrance to Hub (3 diagonal paths)
  ["ENTRANCE", "ICU"],
  ["ENTRANCE", "PHARMACY"],
  ["ENTRANCE", "ROOM_101"],
  // Hub connections
  ["ICU", "PHARMACY"],
  ["ROOM_101", "PHARMACY"],
  // Pharmacy to Emergency
  ["PHARMACY", "EMERGENCY"],
  // Emergency to Storage
  ["EMERGENCY", "STORAGE"]
];

export default function FloorMap({ robots, movingRobots = [] }) {
  const [hoveredWaypoint, setHoveredWaypoint] = useState(null);
  const [robotPositions, setRobotPositions] = useState({});
  const [animatingPaths, setAnimatingPaths] = useState(new Set());

  // Calculate distance between two points
  const calculateDistance = (x1, y1, x2, y2) => {
    return Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
  };

  // Calculate rotation angle for robot facing direction
  const calculateRotation = (fromX, fromY, toX, toY) => {
    const angle = Math.atan2(toY - fromY, toX - fromX) * (180 / Math.PI);
    return angle + 90; // Adjust for robot facing up by default
  };

  // Update robot positions with animation
  useEffect(() => {
    const newPositions = {};
    const newAnimatingPaths = new Set();
    
    robots.forEach(robot => {
      const location = robot.location;
      const waypoint = waypoints[location] || waypoints["ENTRANCE"];
      
      // Check if this robot is moving
      const movingRobot = movingRobots.find(mr => mr.robotId === robot.id);
      
      if (movingRobot && movingRobot.isMoving) {
        const fromWaypoint = waypoints[movingRobot.from] || waypoints["ENTRANCE"];
        const toWaypoint = waypoints[movingRobot.to] || waypoints["ENTRANCE"];
        
        // Add path to animating paths
        const pathKey = `${movingRobot.from}-${movingRobot.to}`;
        newAnimatingPaths.add(pathKey);
        
        // Calculate distance
        const distance = calculateDistance(fromWaypoint.x, fromWaypoint.y, toWaypoint.x, toWaypoint.y);
        const distanceMeters = Math.round(distance * 2); // Approximate meters
        
        newPositions[robot.id] = {
          x: toWaypoint.x,
          y: toWaypoint.y,
          name: robot.name,
          status: robot.status,
          battery: robot.battery,
          isMoving: true,
          rotation: calculateRotation(fromWaypoint.x, fromWaypoint.y, toWaypoint.x, toWaypoint.y),
          distance: distanceMeters,
          from: movingRobot.from,
          to: movingRobot.to
        };
      } else {
        newPositions[robot.id] = {
          x: waypoint.x,
          y: waypoint.y,
          name: robot.name,
          status: robot.status,
          battery: robot.battery,
          isMoving: false,
          rotation: 0,
          distance: 0
        };
      }
    });
    
    setRobotPositions(newPositions);
    setAnimatingPaths(newAnimatingPaths);
  }, [robots, movingRobots]);

  const getWaypointInfo = (location) => {
    const robotsHere = robots.filter(r => {
      const robotWaypoint = waypoints[r.location];
      const locationWaypoint = waypoints[location];
      return robotWaypoint && locationWaypoint && 
             robotWaypoint.x === locationWaypoint.x && 
             robotWaypoint.y === locationWaypoint.y;
    });
    return {
      location,
      robotCount: robotsHere.length,
      robots: robotsHere
    };
  };

  const isPathAnimating = (start, end) => {
    return animatingPaths.has(`${start}-${end}`) || animatingPaths.has(`${end}-${start}`);
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
            <filter id="robotGlow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style={{ stopColor: "#06b6d4", stopOpacity: 0.8 }} />
              <stop offset="100%" style={{ stopColor: "#0ea5e9", stopOpacity: 0.4 }} />
            </linearGradient>
            <linearGradient id="activeLineGradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style={{ stopColor: "#f59e0b", stopOpacity: 1 }} />
              <stop offset="100%" style={{ stopColor: "#ef4444", stopOpacity: 0.8 }} />
            </linearGradient>
          </defs>

          {/* Connection Lines */}
          {connections.map(([start, end], index) => {
            const startPoint = waypoints[start];
            const endPoint = waypoints[end];
            const isActive = isPathAnimating(start, end);
            
            return (
              <g key={index}>
                {/* Base line */}
                <line
                  x1={startPoint.x}
                  y1={startPoint.y}
                  x2={endPoint.x}
                  y2={endPoint.y}
                  stroke="url(#lineGradient)"
                  strokeWidth="0.5"
                  strokeDasharray="2,2"
                  opacity="0.6"
                />
                {/* Animated glowing line when robot is moving */}
                {isActive && (
                  <line
                    x1={startPoint.x}
                    y1={startPoint.y}
                    x2={endPoint.x}
                    y2={endPoint.y}
                    stroke="url(#activeLineGradient)"
                    strokeWidth="1.5"
                    strokeDasharray="4,2"
                    opacity="0.9"
                    filter="url(#glow)"
                    style={{
                      animation: "pathPulse 1.5s ease-in-out infinite"
                    }}
                  />
                )}
              </g>
            );
          })}

          {/* Waypoints */}
          {["ENTRANCE", "PHARMACY", "ICU", "ROOM_101", "EMERGENCY", "STORAGE"].map((location) => {
            const point = waypoints[location];
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
              {/* Pulsing glow for moving robots */}
              {pos.isMoving && (
                <circle
                  cx={pos.x}
                  cy={pos.y}
                  r="5"
                  fill="#f59e0b"
                  opacity="0.4"
                  filter="url(#robotGlow)"
                  style={{
                    animation: "robotPulse 1s ease-in-out infinite",
                    transition: "all 3s cubic-bezier(0.4, 0, 0.2, 1)"
                  }}
                />
              )}
              
              {/* Robot shadow */}
              <ellipse
                cx={pos.x}
                cy={pos.y + 1.5}
                rx="1.5"
                ry="0.5"
                fill="#000"
                opacity="0.2"
                style={{
                  transition: pos.isMoving ? "all 3s cubic-bezier(0.4, 0, 0.2, 1)" : "all 1s cubic-bezier(0.4, 0, 0.2, 1)"
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
                  transition: pos.isMoving ? "all 3s cubic-bezier(0.4, 0, 0.2, 1)" : "all 1s cubic-bezier(0.4, 0, 0.2, 1)",
                  filter: pos.isMoving ? "drop-shadow(0 4px 8px rgba(245, 158, 11, 0.6))" : "drop-shadow(0 2px 4px rgba(0,0,0,0.3))",
                  transform: `rotate(${pos.rotation}deg)`,
                  transformOrigin: "center"
                }}
                onMouseEnter={(e) => {
                  if (!pos.isMoving) {
                    e.currentTarget.style.transform = `rotate(${pos.rotation}deg) scale(1.3)`;
                  }
                }}
                onMouseLeave={(e) => {
                  if (!pos.isMoving) {
                    e.currentTarget.style.transform = `rotate(${pos.rotation}deg) scale(1)`;
                  }
                }}
              >
                🤖
              </text>
              
              {/* Distance indicator for moving robots */}
              {pos.isMoving && pos.distance > 0 && (
                <g>
                  <rect
                    x={pos.x - 6}
                    y={pos.y - 8}
                    width="12"
                    height="4"
                    fill="#f59e0b"
                    rx="2"
                    opacity="0.9"
                    style={{
                      transition: "all 3s cubic-bezier(0.4, 0, 0.2, 1)"
                    }}
                  />
                  <text
                    x={pos.x}
                    y={pos.y - 5.5}
                    textAnchor="middle"
                    fontSize="2"
                    fontWeight="bold"
                    fill="#fff"
                    className="pointer-events-none select-none"
                  >
                    {pos.distance}m
                  </text>
                </g>
              )}
              
              {/* Robot name */}
              <text
                x={pos.x}
                y={pos.y + (pos.isMoving ? 6 : 5)}
                textAnchor="middle"
                fontSize="1.8"
                fontWeight="600"
                fill="#1e293b"
                className="pointer-events-none select-none"
                style={{
                  textShadow: "0 0 4px rgba(255,255,255,0.9)",
                  transition: pos.isMoving ? "all 3s cubic-bezier(0.4, 0, 0.2, 1)" : "all 1s cubic-bezier(0.4, 0, 0.2, 1)"
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
        
        @keyframes pathPulse {
          0%, 100% {
            opacity: 0.9;
            stroke-width: 1.5;
          }
          50% {
            opacity: 0.6;
            stroke-width: 2;
          }
        }
        
        @keyframes robotPulse {
          0%, 100% {
            opacity: 0.4;
            transform: scale(1);
          }
          50% {
            opacity: 0.7;
            transform: scale(1.3);
          }
        }
      `}</style>
    </div>
  );
}