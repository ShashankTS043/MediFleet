import { Bot, Zap, Shield, BarChart, Users, Heart } from "lucide-react";

export default function About() {
  const team = [
    { name: "Dr. Sarah Chen", role: "Project Lead", expertise: "Healthcare Robotics" },
    { name: "Michael Rodriguez", role: "Lead Developer", expertise: "Full Stack Development" },
    { name: "Emily Johnson", role: "UX Designer", expertise: "Healthcare UI/UX" },
    { name: "David Kim", role: "AI Specialist", expertise: "Robot Coordination" }
  ];
  
  const technologies = [
    { name: "React", description: "Modern frontend framework" },
    { name: "FastAPI", description: "High-performance backend" },
    { name: "MongoDB", description: "Flexible database solution" },
    { name: "WebSocket", description: "Real-time communication" }
  ];
  
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-slate-800 mb-4" data-testid="about-title">
            About MediFleet
          </h1>
          <p className="text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Transforming hospital logistics through intelligent robot coordination and real-time tracking
          </p>
        </div>
        
        {/* Mission */}
        <div className="glass rounded-3xl p-8 md:p-12 mb-12">
          <div className="flex items-center space-x-3 mb-6">
            <Heart className="w-8 h-8 text-cyan-600" />
            <h2 className="text-2xl font-bold text-slate-800">Our Mission</h2>
          </div>
          <p className="text-slate-700 leading-relaxed mb-4">
            MediFleet is designed to revolutionize hospital operations by providing an intelligent, automated
            system for coordinating robot logistics. Our platform ensures efficient delivery of medical supplies,
            specimens, and equipment throughout healthcare facilities.
          </p>
          <p className="text-slate-700 leading-relaxed">
            By leveraging advanced algorithms and real-time tracking, we minimize response times, optimize
            robot utilization, and ultimately contribute to better patient care outcomes.
          </p>
        </div>
        
        {/* Key Features */}
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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {technologies.map((tech, index) => (
              <div key={index} className="glass rounded-xl p-6 text-center card-hover">
                <div className="text-2xl font-bold text-cyan-600 mb-2">{tech.name}</div>
                <div className="text-sm text-slate-600">{tech.description}</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* Team */}
        <div>
          <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">Our Team</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {team.map((member, index) => (
              <div key={index} className="glass rounded-2xl p-6 text-center card-hover" data-testid={`team-member-${index}`}>
                <div className="w-20 h-20 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-full mx-auto mb-4 flex items-center justify-center text-white text-2xl font-bold">
                  {member.name.split(' ').map(n => n[0]).join('')}
                </div>
                <h3 className="font-semibold text-slate-800 mb-1">{member.name}</h3>
                <p className="text-sm text-cyan-600 font-medium mb-2">{member.role}</p>
                <p className="text-xs text-slate-600">{member.expertise}</p>
              </div>
            ))}
          </div>
        </div>
        
        {/* Contact */}
        <div className="mt-12 glass rounded-2xl p-8 text-center">
          <h2 className="text-2xl font-bold text-slate-800 mb-4">Get In Touch</h2>
          <p className="text-slate-600 mb-6">
            Interested in implementing MediFleet at your healthcare facility?
          </p>
          <button className="btn-primary" data-testid="contact-btn">
            Contact Us
          </button>
        </div>
      </div>
    </div>
  );
}