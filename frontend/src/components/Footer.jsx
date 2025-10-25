import { Activity, Github, Linkedin, Mail } from "lucide-react";

export default function Footer() {
  return (
    <footer className="glass mt-20 border-t border-cyan-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
                MediFleet
              </span>
            </div>
            <p className="text-slate-600 text-sm leading-relaxed">
              Advanced hospital robot logistics coordination system for efficient healthcare operations.
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold text-slate-800 mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li><a href="/" className="hover:text-cyan-600 transition-colors">Home</a></li>
              <li><a href="/dashboard" className="hover:text-cyan-600 transition-colors">Dashboard</a></li>
              <li><a href="/robots" className="hover:text-cyan-600 transition-colors">Robots</a></li>
              <li><a href="/analytics" className="hover:text-cyan-600 transition-colors">Analytics</a></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold text-slate-800 mb-4">Team Info</h3>
            <p className="text-slate-600 text-sm mb-4">
              Built by the MediFleet Team<br />
              Healthcare Innovation Lab<br />
              2025
            </p>
            <div className="flex space-x-3">
              <a href="#" className="w-9 h-9 rounded-full bg-cyan-50 flex items-center justify-center text-cyan-600 hover:bg-cyan-100 transition-colors" data-testid="footer-github">
                <Github className="w-4 h-4" />
              </a>
              <a href="#" className="w-9 h-9 rounded-full bg-cyan-50 flex items-center justify-center text-cyan-600 hover:bg-cyan-100 transition-colors" data-testid="footer-linkedin">
                <Linkedin className="w-4 h-4" />
              </a>
              <a href="#" className="w-9 h-9 rounded-full bg-cyan-50 flex items-center justify-center text-cyan-600 hover:bg-cyan-100 transition-colors" data-testid="footer-mail">
                <Mail className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
        
        <div className="border-t border-cyan-100 mt-8 pt-8 text-center text-sm text-slate-600">
          <p>&copy; 2025 MediFleet. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}