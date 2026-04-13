import React from 'react';
import { Settings, Bell, User } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="flex items-center justify-between px-6 py-4 bg-[#101214] border-b border-brand-panel-border">
      <div className="flex items-center space-x-12">
        <h1 className="text-brand-cyan text-xl font-bold tracking-[0.15em] pl-2 drop-shadow-[0_0_8px_rgba(0,210,211,0.5)]">
          INDUSTRIE IA
        </h1>
      </div>

      <div className="flex items-center space-x-6 text-brand-text-muted">
        <button className="hover:text-white transition-colors">
          <Settings size={20} />
        </button>
        <button className="hover:text-white transition-colors relative">
          <Bell size={20} />
          {/* Cyan Notification Dot */}
          <span className="absolute -top-1 -right-1 w-2.5 h-2.5 bg-brand-cyan rounded-full border-[2px] border-[#101214]"></span>
        </button>
        <div className="w-8 h-8 rounded bg-brand-panel border border-brand-panel-border overflow-hidden">
          {/* Placeholder for avatar */}
          <div className="w-full h-full bg-slate-800 flex items-center justify-center">
            <User size={18} className="text-slate-400" />
          </div>
        </div>
      </div>
    </nav>
  );
}
