import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { MapPin, AlertCircle, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";
import BiddingModal from "@/components/BiddingModal";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function CreateTask() {
  const navigate = useNavigate();
  const [destination, setDestination] = useState("");
  const [priority, setPriority] = useState("medium");
  const [loading, setLoading] = useState(false);
  const [showBiddingModal, setShowBiddingModal] = useState(false);
  const [robots, setRobots] = useState([]);
  const [createdTaskId, setCreatedTaskId] = useState(null);
  
  const destinations = [
    "Emergency Room",
    "Surgery Wing",
    "ICU",
    "Pharmacy",
    "Laboratory",
    "Radiology",
    "Pediatrics",
    "Cardiology",
    "Oncology",
    "Neurology"
  ];
  
  const priorities = [
    { value: "low", label: "Low", color: "from-blue-500 to-cyan-500" },
    { value: "medium", label: "Medium", color: "from-yellow-500 to-orange-500" },
    { value: "high", label: "High", color: "from-orange-500 to-red-500" },
    { value: "urgent", label: "Urgent", color: "from-red-500 to-pink-500" }
  ];
  
  // Fetch robots on mount
  useEffect(() => {
    const fetchRobots = async () => {
      try {
        const response = await axios.get(`${API}/robots`);
        setRobots(response.data);
      } catch (error) {
        console.error("Error fetching robots:", error);
      }
    };
    
    fetchRobots();
  }, []);
  
  // Poll task status to detect when bidding starts
  useEffect(() => {
    if (!createdTaskId) return;
    
    const checkTaskStatus = async () => {
      try {
        const response = await axios.get(`${API}/tasks/${createdTaskId}`);
        const task = response.data;
        
        if (task.status === "bidding") {
          setShowBiddingModal(true);
          setCreatedTaskId(null); // Stop polling
        }
      } catch (error) {
        console.error("Error checking task status:", error);
      }
    };
    
    const interval = setInterval(checkTaskStatus, 500);
    
    return () => clearInterval(interval);
  }, [createdTaskId]);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!destination) {
      toast.error("Please select a destination");
      return;
    }
    
    setLoading(true);
    
    try {
      const response = await axios.post(`${API}/tasks`, {
        destination,
        priority
      });
      
      toast.success("Task created successfully! Robot bidding initiated.");
      setCreatedTaskId(response.data.id);
    } catch (error) {
      console.error("Error creating task:", error);
      toast.error("Failed to create task. Please try again.");
      setLoading(false);
    }
  };
  
  const handleModalClose = () => {
    setShowBiddingModal(false);
    setLoading(false);
    setTimeout(() => {
      navigate("/dashboard");
    }, 500);
  };
  
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-800 mb-3" data-testid="create-task-title">
            Create New Task
          </h1>
          <p className="text-base text-slate-600">
            Assign a delivery task - robots will automatically bid for it
          </p>
        </div>
        
        <div className="glass rounded-3xl p-8 md:p-10">
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Destination */}
            <div>
              <label className="flex items-center space-x-2 text-slate-700 font-semibold mb-3">
                <MapPin className="w-5 h-5 text-cyan-600" />
                <span>Destination</span>
              </label>
              <select
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border-2 border-cyan-100 focus:border-cyan-500 focus:outline-none bg-white text-slate-700 transition-colors"
                data-testid="task-destination-select"
              >
                <option value="">Select destination...</option>
                {destinations.map((dest) => (
                  <option key={dest} value={dest}>
                    {dest}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Priority */}
            <div>
              <label className="flex items-center space-x-2 text-slate-700 font-semibold mb-3">
                <AlertCircle className="w-5 h-5 text-cyan-600" />
                <span>Priority Level</span>
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {priorities.map((p) => (
                  <button
                    key={p.value}
                    type="button"
                    onClick={() => setPriority(p.value)}
                    data-testid={`priority-${p.value}-btn`}
                    className={`p-4 rounded-xl border-2 transition-all ${
                      priority === p.value
                        ? `bg-gradient-to-r ${p.color} text-white border-transparent shadow-lg`
                        : "bg-white border-slate-200 text-slate-700 hover:border-cyan-300"
                    }`}
                  >
                    <div className="font-semibold">{p.label}</div>
                  </button>
                ))}
              </div>
            </div>
            
            {/* Info Box */}
            <div className="bg-cyan-50 border border-cyan-200 rounded-xl p-4">
              <div className="flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 text-cyan-600 mt-0.5 flex-shrink-0" />
                <div className="text-sm text-slate-700">
                  <p className="font-semibold mb-1">Automatic Robot Assignment</p>
                  <p className="text-slate-600">
                    Once created, available robots will automatically bid for this task based on their
                    battery level and location. The best-suited robot will be assigned within seconds.
                  </p>
                </div>
              </div>
            </div>
            
            {/* Buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="create-task-submit-btn"
              >
                {loading ? "Creating Task..." : "Create Task"}
              </button>
              <button
                type="button"
                onClick={() => navigate("/dashboard")}
                className="flex-1 px-6 py-3 rounded-full border-2 border-slate-300 text-slate-700 font-semibold hover:bg-slate-50 transition-colors"
                data-testid="create-task-cancel-btn"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
      
      {/* Bidding Modal */}
      <BiddingModal 
        isOpen={showBiddingModal}
        onClose={handleModalClose}
        robots={robots}
        destination={destination}
      />
    </div>
  );
}