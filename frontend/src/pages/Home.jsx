import { ArrowRight, Bot, Zap, Shield, BarChart } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();
  
  const features = [
    {
      icon: Bot,
      title: "Automated Robot Bidding",
      description: "Intelligent robot selection based on battery, location, and availability"
    },
    {
      icon: Zap,
      title: "Real-Time Tracking",
      description: "Monitor task progression from pending to completion with live updates"
    },
    {
      icon: Shield,
      title: "Reliable Operations",
      description: "99.8% system uptime ensuring continuous healthcare logistics"
    },
    {
      icon: BarChart,
      title: "Advanced Analytics",
      description: "Comprehensive insights with charts and performance metrics"
    }
  ];
  
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-50 via-blue-50 to-transparent opacity-60"></div>
        
        <div className="relative max-w-7xl mx-auto">
          <div className="text-center fade-in">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-slate-800 mb-6" data-testid="hero-title">
              Hospital Robot Logistics
              <span className="block mt-2 bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                Coordination System
              </span>
            </h1>
            <p className="text-base sm:text-lg text-slate-600 mb-8 max-w-2xl mx-auto leading-relaxed">
              MediFleet streamlines hospital operations with intelligent robot task assignment,
              real-time tracking, and comprehensive analytics for optimal healthcare logistics.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate("/create-task")}
                className="btn-primary inline-flex items-center space-x-2"
                data-testid="hero-create-task-btn"
              >
                <span>Create Task</span>
                <ArrowRight className="w-5 h-5" />
              </button>
              <button
                onClick={() => navigate("/dashboard")}
                className="px-8 py-3 rounded-full border-2 border-cyan-500 text-cyan-700 font-semibold hover:bg-cyan-50 transition-colors"
                data-testid="hero-dashboard-btn"
              >
                View Dashboard
              </button>
            </div>
          </div>
          
          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { label: "Active Robots", value: "4+" },
              { label: "Tasks Completed", value: "750+" },
              { label: "Avg Response", value: "3.5min" },
              { label: "Uptime", value: "99.8%" }
            ].map((stat, index) => (
              <div key={index} className="glass rounded-2xl p-6 text-center card-hover" data-testid={`stat-${stat.label.toLowerCase().replace(' ', '-')}`}>
                <div className="text-3xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                  {stat.value}
                </div>
                <div className="text-sm text-slate-600 mt-2">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-slate-800 mb-4" data-testid="features-title">
              Powerful Features
            </h2>
            <p className="text-base text-slate-600 max-w-2xl mx-auto">
              Everything you need to manage hospital robot logistics efficiently
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="glass rounded-2xl p-6 card-hover" data-testid={`feature-${index}`}>
                  <div className="w-12 h-12 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-xl flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-2">{feature.title}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>
      
      {/* Project Overview */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-cyan-50 to-blue-50">
        <div className="max-w-4xl mx-auto glass rounded-3xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-slate-800 mb-6" data-testid="overview-title">
            Project Overview
          </h2>
          <div className="space-y-4 text-slate-700 leading-relaxed">
            <p>
              MediFleet is a comprehensive hospital robot logistics coordination system designed to optimize
              healthcare operations through intelligent automation and real-time monitoring.
            </p>
            <p>
              The system features an automated bidding mechanism where robots compete for task assignments based
              on their current battery levels, location proximity, and availability. Tasks progress through
              clearly defined stages: Pending → Bidding → Assigned → Moving → Completed.
            </p>
            <p>
              With advanced analytics dashboards, hospital administrators can track performance metrics, monitor
              robot efficiency, and make data-driven decisions to improve operational workflows. The platform
              ensures reliable 24/7 operations with minimal downtime.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}