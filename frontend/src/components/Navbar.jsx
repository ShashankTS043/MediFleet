import { Link, useLocation } from "react-router-dom";
import { Activity, Plus, LayoutDashboard, Bot, BarChart3, Info } from "lucide-react";

export default function Navbar() {
  const location = useLocation();
  
  const navLinks = [
    { path: "/", label: "Home", icon: Activity },
    { path: "/create-task", label: "Create Task", icon: Plus },
    { path: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { path: "/robots", label: "Robots", icon: Bot },
    { path: "/analytics", label: "Analytics", icon: BarChart3 },
    { path: "/about", label: "About", icon: Info },
  ];
  
  return (
    <nav className="glass sticky top-0 z-50 border-b border-cyan-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2" data-testid="nav-logo">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
              MediFleet
            </span>
          </Link>
          
          <div className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  data-testid={`nav-${link.label.toLowerCase().replace(' ', '-')}`}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                    isActive
                      ? "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg"
                      : "text-slate-600 hover:bg-cyan-50 hover:text-cyan-700"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="font-medium">{link.label}</span>
                </Link>
              );
            })}
          </div>
          
          <div className="md:hidden">
            <button className="text-slate-600 p-2" data-testid="nav-mobile-menu">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}