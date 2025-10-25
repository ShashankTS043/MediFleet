import { useEffect, useState } from "react";
import { Trophy, MapPin, Zap } from "lucide-react";

export default function BiddingModal({ isOpen, onClose, robots, destination }) {
  const [scores, setScores] = useState({});
  const [winner, setWinner] = useState(null);
  const [showWinner, setShowWinner] = useState(false);
  
  // Calculate distances and bid scores
  const calculateDistance = (location) => {
    // Simulated distance calculation (in meters)
    const distances = {
      "Emergency Room": { "Emergency Room": 0, "Surgery Wing": 120, "ICU": 85, "Charging Station": 150 },
      "Surgery Wing": { "Emergency Room": 120, "Surgery Wing": 0, "ICU": 95, "Charging Station": 110 },
      "ICU": { "Emergency Room": 85, "Surgery Wing": 95, "ICU": 0, "Charging Station": 140 },
      "Pharmacy": { "Emergency Room": 100, "Surgery Wing": 130, "ICU": 115, "Charging Station": 90 },
      "Laboratory": { "Emergency Room": 110, "Surgery Wing": 80, "ICU": 125, "Charging Station": 100 },
      "Radiology": { "Emergency Room": 95, "Surgery Wing": 105, "ICU": 90, "Charging Station": 120 },
      "Pediatrics": { "Emergency Room": 130, "Surgery Wing": 70, "ICU": 135, "Charging Station": 95 },
      "Cardiology": { "Emergency Room": 105, "Surgery Wing": 115, "ICU": 100, "Charging Station": 110 },
      "Oncology": { "Emergency Room": 125, "Surgery Wing": 90, "ICU": 120, "Charging Station": 105 },
      "Neurology": { "Emergency Room": 115, "Surgery Wing": 100, "ICU": 110, "Charging Station": 125 },
      "Charging Station": { "Emergency Room": 150, "Surgery Wing": 110, "ICU": 140, "Charging Station": 0 }
    };
    
    const destDistances = distances[destination] || {};
    return destDistances[location] || Math.floor(Math.random() * 100) + 50;
  };
  
  const robotsWithData = robots
    .filter(r => r.status === "idle" || r.status === "busy")
    .map(robot => {
      const distance = calculateDistance(robot.location);
      const bidScore = Math.round((1000 / distance) * robot.battery / 100);
      return {
        ...robot,
        distance,
        bidScore
      };
    });
  
  useEffect(() => {
    if (!isOpen) {
      setScores({});
      setWinner(null);
      setShowWinner(false);
      return;
    }
    
    // Animate scores counting up
    const duration = 2000;
    const steps = 50;
    const stepDuration = duration / steps;
    
    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      
      const newScores = {};
      robotsWithData.forEach(robot => {
        newScores[robot.id] = Math.round(robot.bidScore * progress);
      });
      
      setScores(newScores);
      
      if (currentStep >= steps) {
        clearInterval(interval);
        
        // Determine winner
        const winningRobot = robotsWithData.reduce((prev, current) => 
          current.bidScore > prev.bidScore ? current : prev
        );
        
        setTimeout(() => {
          setWinner(winningRobot);
          setShowWinner(true);
          
          // Auto-close after showing winner
          setTimeout(() => {
            onClose();
          }, 3000);
        }, 500);
      }
    }, stepDuration);
    
    return () => clearInterval(interval);
  }, [isOpen]);
  
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" style={{ animation: "fadeIn 0.3s ease-out" }}>
      {/* Overlay */}
      <div 
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
        onClick={onClose}
      ></div>
      
      {/* Modal */}
      <div className="relative glass rounded-3xl p-8 max-w-4xl w-full shadow-2xl" style={{ animation: "slideUp 0.4s ease-out" }}>
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full flex items-center justify-center animate-pulse">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-slate-800" data-testid="bidding-modal-title">
              Bidding in Progress
            </h2>
          </div>
          <p className="text-slate-600">Robots competing for task assignment</p>
        </div>
        
        {/* Winner Banner */}
        {showWinner && winner && (
          <div 
            className="mb-6 bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-4 text-center"
            style={{ animation: "bounceIn 0.5s ease-out" }}
            data-testid="winner-banner"
          >
            <div className="flex items-center justify-center space-x-3">
              <Trophy className="w-8 h-8 text-white" />
              <span className="text-2xl font-bold text-white">
                Winner: {winner.name}
              </span>
              <Trophy className="w-8 h-8 text-white" />
            </div>
          </div>
        )}
        
        {/* Robots Table */}
        <div className="overflow-hidden rounded-2xl border-2 border-cyan-100">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white">
                <th className="px-6 py-4 text-left font-semibold">Robot ID</th>
                <th className="px-6 py-4 text-left font-semibold">Location</th>
                <th className="px-6 py-4 text-right font-semibold">Distance (m)</th>
                <th className="px-6 py-4 text-right font-semibold">Bid Score</th>
                <th className="px-6 py-4 text-center font-semibold">Status</th>
              </tr>
            </thead>
            <tbody>
              {robotsWithData.map((robot, index) => {
                const isWinner = winner && winner.id === robot.id;
                const currentScore = scores[robot.id] || 0;
                
                return (
                  <tr
                    key={robot.id}
                    className={`transition-all duration-500 ${
                      isWinner 
                        ? "bg-green-50 border-l-4 border-green-500" 
                        : "bg-white hover:bg-cyan-50"
                    }`}
                    style={{ animation: `slideIn 0.3s ease-out ${index * 0.1}s both` }}
                    data-testid={`bidding-robot-${robot.id}`}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center text-white font-bold">
                          {robot.name.split('-')[1]}
                        </div>
                        <span className="font-semibold text-slate-800">{robot.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2 text-slate-700">
                        <MapPin className="w-4 h-4 text-cyan-600" />
                        <span>{robot.location}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right font-mono text-slate-700">
                      {robot.distance}m
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <div className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                          {currentScore}
                        </div>
                        {isWinner && (
                          <Trophy className="w-5 h-5 text-green-600 animate-bounce" />
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center">
                        {isWinner ? (
                          <span className="px-3 py-1 rounded-full bg-green-500 text-white text-sm font-semibold">
                            WINNER
                          </span>
                        ) : (
                          <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse"></div>
                            <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }}></div>
                            <div className="w-2 h-2 bg-cyan-500 rounded-full animate-pulse" style={{ animationDelay: "0.4s" }}></div>
                          </div>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        
        {/* Footer */}
        <div className="mt-6 text-center text-sm text-slate-600">
          <p>Highest bid score wins • Score = (1000 / Distance) × (Battery / 100)</p>
        </div>
      </div>
      
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(40px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-20px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
        
        @keyframes bounceIn {
          0% {
            opacity: 0;
            transform: scale(0.3);
          }
          50% {
            opacity: 1;
            transform: scale(1.05);
          }
          70% {
            transform: scale(0.9);
          }
          100% {
            transform: scale(1);
          }
        }
      `}</style>
    </div>
  );
}