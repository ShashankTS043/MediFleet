import { Bot, Zap, Shield, BarChart, Users, Heart, Github, ExternalLink, Code } from "lucide-react";

export default function About() {
  const team = [
    { name: "Shashank T S", role: "Project Lead & Backend Developer", expertise: "FastAPI, MongoDB, System Architecture", avatar: "ST" },
    { name: "Shreekesh S", role: "Frontend Developer & UI/UX Designer", expertise: "React, Design Systems, User Experience", avatar: "SS" },
    { name: "Rahul C", role: "Hardware Integration & IoT Specialist", expertise: "ESP32, MQTT, Embedded Systems", avatar: "RC" }
  ];
  
  const techStack = [
    { category: "Hardware", items: ["ESP32 Microcontroller", "Motor Controllers", "Ultrasonic Sensors"] },
    { category: "Communication", items: ["MQTT Protocol", "WebSocket", "REST API"] },
    { category: "Backend", items: ["FastAPI (Python)", "MongoDB", "Motor (Async Driver)"] },
    { category: "Frontend", items: ["React 18", "Tailwind CSS", "Shadcn/UI"] }
  ];
  
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 fade-in">
          <h1 className="text-4xl font-bold text-slate-800 mb-4" data-testid="about-title">
            About MediFleet
          </h1>
          <p className="text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Advanced hospital robot logistics coordination system for efficient healthcare operations
          </p>
        </div>
        
        {/* Project Overview */}
        <div className="glass rounded-3xl p-8 md:p-12 mb-12 card-hover">
          <div className="flex items-center space-x-3 mb-6">
            <Heart className="w-8 h-8 text-cyan-600" />
            <h2 className="text-2xl font-bold text-slate-800">Project Overview</h2>
          </div>
          <div className="space-y-4 text-slate-700 leading-relaxed">
            <p>
              MediFleet is a comprehensive hospital robot logistics coordination system designed to optimize
              healthcare operations through intelligent automation and real-time monitoring. Developed as part of
              a hackathon challenge to revolutionize hospital operations.
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
          
          {/* Hackathon Info */}
          <div className="mt-8 p-6 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-2xl border-2 border-cyan-200">
            <h3 className="text-lg font-bold text-slate-800 mb-3">🏆 Hackathon Project</h3>
            <p className="text-slate-700 mb-4">
              This project was developed for a healthcare innovation hackathon, addressing the critical need for
              efficient hospital logistics and autonomous robot coordination systems.
            </p>
            <div className="flex flex-wrap gap-3">
              <a href="https://github.com/medifleet" target="_blank" rel="noopener noreferrer" 
                 className="inline-flex items-center space-x-2 px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 transition-colors">
                <Github className="w-4 h-4" />
                <span>View on GitHub</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <a href="/mqtt-docs" 
                 className="inline-flex items-center space-x-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors">
                <Code className="w-4 h-4" />
                <span>MQTT Integration Docs</span>
              </a>
            </div>
          </div>
        </div>
        
        {/* Key Capabilities */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Key Capabilities</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              {
                icon: Bot,
                title: "Intelligent Bidding System",
                description: "Robots automatically compete for tasks based on battery level, location, and current workload, ensuring optimal assignment."
              },
              {
                icon: Zap,
                title: "Real-Time Tracking",
                description: "Monitor every task from creation to completion with live status updates and detailed progression tracking."
              },
              {
                icon: Shield,
                title: "High Reliability",
                description: "Built for 24/7 operation with 99.8% uptime, ensuring continuous service in critical healthcare environments."
              },
              {
                icon: BarChart,
                title: "Advanced Analytics",
                description: "Comprehensive dashboards with performance metrics, charts, and insights for data-driven decision making."
              }
            ].map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="glass rounded-2xl p-6 card-hover">
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
        
        {/* Technology Stack */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Technology Stack</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {techStack.map((stack, index) => (
              <div key={index} className="glass rounded-xl p-6 card-hover">
                <h3 className="font-bold text-slate-800 mb-4 text-center">{stack.category}</h3>
                <ul className="space-y-2">
                  {stack.items.map((item, idx) => (
                    <li key={idx} className="text-sm text-slate-600 flex items-center space-x-2">
                      <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full"></div>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
        
        {/* Team */}
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Our Team</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {team.map((member, index) => (
              <div key={index} className="glass rounded-2xl p-6 text-center card-hover" data-testid={`team-member-${index}`}>
                <div className="w-24 h-24 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                  {member.avatar}
                </div>
                <h3 className="font-bold text-slate-800 mb-1 text-lg">{member.name}</h3>
                <p className="text-sm text-cyan-600 font-semibold mb-3">{member.role}</p>
                <p className="text-xs text-slate-600 leading-relaxed">{member.expertise}</p>
              </div>
            ))}
          </div>
        </div>
        
        {/* Contact */}
        <div className="mt-12 glass rounded-2xl p-8 text-center card-hover">
          <h2 className="text-2xl font-bold text-slate-800 mb-4">Get In Touch</h2>
          <p className="text-slate-600 mb-6">
            Interested in implementing MediFleet at your healthcare facility or collaborating on this project?
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <button className="btn-primary" data-testid="contact-btn">
              Contact Us
            </button>
            <a href="/api-docs" className="px-6 py-3 rounded-full border-2 border-cyan-500 text-cyan-700 font-semibold hover:bg-cyan-50 transition-colors">
              View API Documentation
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}