import React from 'react';
import { LayoutDashboard, MapPin, ShieldCheck } from 'lucide-react';

interface NavbarProps {
  activeTab: 'merchant' | 'search' | 'scan';
  setActiveTab: (tab: 'merchant' | 'search' | 'scan') => void;
  isBackendConnected: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, isBackendConnected }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/95 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Tagline */}
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('merchant')}>
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-md">
            <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight text-white font-outfit">SHOPWISE AI</span>
            </div>
            <p className="text-[11px] text-slate-400 font-medium tracking-wide">Real-Time Commerce Intelligence</p>
          </div>
        </div>

        {/* Primary Mode Navigation Tabs */}
        <nav className="flex items-center space-x-1 bg-slate-950 p-1.5 rounded-xl border border-slate-800/80">
          <button
            onClick={() => setActiveTab('merchant')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'merchant'
                ? 'bg-cyan-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Merchant Intelligence</span>
          </button>

          <button
            onClick={() => setActiveTab('search')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'search'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <MapPin className="w-3.5 h-3.5" />
            <span>Local Discovery</span>
          </button>

          <button
            onClick={() => setActiveTab('scan')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 text-xs font-bold rounded-lg transition-all ${
              activeTab === 'scan'
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Verify Product</span>
          </button>
        </nav>

        {/* Status Indicator */}
        <div className="hidden md:flex items-center space-x-2 text-[11px] text-slate-400 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800/80 font-mono">
          <span className={`w-2 h-2 rounded-full ${isBackendConnected ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
          <span>{isBackendConnected ? 'System Ready' : 'Connecting'}</span>
        </div>

      </div>
    </header>
  );
};
