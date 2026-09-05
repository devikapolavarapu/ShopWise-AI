import React, { useState } from 'react';
import { Search, Sparkles, SlidersHorizontal } from 'lucide-react';

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({ onSearch, isLoading }) => {
  const [inputQuery, setInputQuery] = useState("Find fresh Amul milk under 70 rupees within 3 km");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputQuery.trim()) {
      onSearch(inputQuery);
    }
  };

  const handleChipClick = (presetQuery: string) => {
    setInputQuery(presetQuery);
    onSearch(presetQuery);
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3">
      <form onSubmit={handleSubmit} className="relative flex items-center">
        <div className="absolute left-4 text-cyan-400">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <input
          type="text"
          value={inputQuery}
          onChange={(e) => setInputQuery(e.target.value)}
          placeholder="Ask ShopWise: e.g. Find fresh Amul milk under ₹70 within 3 km..."
          className="w-full py-4 pl-12 pr-32 bg-slate-900/90 text-white placeholder-slate-400 rounded-2xl border border-cyan-500/30 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 shadow-xl shadow-cyan-950/20 text-base"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="absolute right-2 px-6 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold rounded-xl shadow-md transition-all flex items-center gap-2 text-sm disabled:opacity-50"
        >
          {isLoading ? (
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          <span>{isLoading ? 'Parsing...' : 'Find Nearby'}</span>
        </button>
      </form>

      {/* Preset Search Chips */}
      <div className="flex flex-wrap items-center gap-2 text-xs text-slate-400 pt-1">
        <span className="font-medium text-slate-500 flex items-center gap-1">
          <SlidersHorizontal className="w-3 h-3" /> Try queries:
        </span>
        <button
          onClick={() => handleChipClick("Find fresh Amul milk under 70 rupees within 3 km")}
          className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-cyan-300 rounded-lg border border-slate-800 transition"
        >
          🥛 Fresh Amul Milk &lt; ₹70
        </button>
        <button
          onClick={() => handleChipClick("100% whole wheat Britannia bread within 2 km")}
          className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-cyan-300 rounded-lg border border-slate-800 transition"
        >
          🍞 Britannia Bread nearby
        </button>
        <button
          onClick={() => handleChipClick("Aashirvaad Atta 5kg under 280 rupees")}
          className="px-3 py-1 bg-slate-900 hover:bg-slate-800 text-cyan-300 rounded-lg border border-slate-800 transition"
        >
          🌾 Aashirvaad Atta 5kg
        </button>
      </div>
    </div>
  );
};
