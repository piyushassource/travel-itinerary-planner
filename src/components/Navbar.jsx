import React from 'react';
import { Compass, Sparkles, Server, Bookmark, Database } from 'lucide-react';

export default function Navbar({ backendStatus, activeTab, onTabChange, savedTripsCount }) {
  return (
    <header className="sticky top-0 z-30 bg-white/85 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-600 to-emerald-500 flex items-center justify-center text-white shadow-md shadow-teal-500/20">
            <Compass className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-slate-900">TravelPulse AI</span>
              <span className="text-[10px] font-semibold uppercase tracking-wider bg-teal-50 text-teal-700 px-2 py-0.5 rounded-full border border-teal-200">
                GenAI & Supabase
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">Persistent Multi-Scenario Itinerary Management</p>
          </div>
        </div>

        {/* View Switcher Tabs (Planner vs Saved Trips) */}
        <div className="flex items-center bg-slate-100 p-1 rounded-2xl border border-slate-200">
          <button
            onClick={() => onTabChange('planner')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'planner'
                ? 'bg-white text-teal-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Trip Planner</span>
          </button>

          <button
            onClick={() => onTabChange('saved_trips')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
              activeTab === 'saved_trips'
                ? 'bg-white text-teal-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <Bookmark className="w-3.5 h-3.5" />
            <span>Saved Trips</span>
            <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] bg-teal-100 text-teal-800">
              {savedTripsCount}
            </span>
          </button>
        </div>

        {/* System & DB Status Badge */}
        <div className="hidden md:flex items-center gap-2">
          <div className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 text-slate-600">
            <Database className="w-3.5 h-3.5 text-emerald-600" />
            <span className="font-medium text-[11px]">
              {backendStatus?.supabase_configured ? 'Supabase Connected' : 'Persistent Storage Active'}
            </span>
          </div>
        </div>

      </div>
    </header>
  );
}
