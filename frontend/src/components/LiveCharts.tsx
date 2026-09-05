import React from 'react';
import { TimeSeriesPoint } from '../types';
import { TrendingUp, CreditCard, ShoppingBag, DollarSign } from 'lucide-react';

interface LiveChartsProps {
  points: TimeSeriesPoint[];
}

export const LiveCharts: React.FC<LiveChartsProps> = ({ points }) => {
  if (!points || points.length === 0) return null;

  const maxRev = Math.max(100, ...points.map(p => p.revenue));
  const maxUnits = Math.max(5, ...points.map(p => p.units));

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      
      {/* Chart 1: Revenue Timeline (30 Min) */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5 font-outfit">
            <DollarSign className="w-4 h-4 text-emerald-400" /> Revenue (Last 30 Min)
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Live Ingestion</span>
        </div>

        <div className="h-28 flex items-end justify-between gap-1 pt-4 border-b border-slate-800/80 pb-1">
          {points.map((pt, idx) => {
            const heightPct = Math.min(100, Math.max(10, (pt.revenue / maxRev) * 100));
            return (
              <div key={idx} className="flex-1 flex flex-col items-center group relative">
                <div
                  style={{ height: `${heightPct}%` }}
                  className="w-full bg-gradient-to-t from-emerald-600 to-emerald-400 rounded-t transition-all group-hover:bg-emerald-300"
                />
                <span className="text-[9px] text-slate-500 font-mono mt-1 opacity-80">{pt.time}</span>

                {/* Tooltip */}
                <div className="absolute bottom-full mb-1 hidden group-hover:flex flex-col items-center bg-slate-950 text-white text-[10px] p-1.5 rounded border border-slate-800 shadow-xl z-20 whitespace-nowrap">
                  <span>{pt.time}</span>
                  <span className="font-bold text-emerald-400">₹{pt.revenue}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart 2: Units Sold Timeline (30 Min) */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5 font-outfit">
            <ShoppingBag className="w-4 h-4 text-cyan-400" /> Units Sold (Last 30 Min)
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Live Ingestion</span>
        </div>

        <div className="h-28 flex items-end justify-between gap-1 pt-4 border-b border-slate-800/80 pb-1">
          {points.map((pt, idx) => {
            const heightPct = Math.min(100, Math.max(10, (pt.units / maxUnits) * 100));
            return (
              <div key={idx} className="flex-1 flex flex-col items-center group relative">
                <div
                  style={{ height: `${heightPct}%` }}
                  className="w-full bg-gradient-to-t from-cyan-600 to-cyan-400 rounded-t transition-all group-hover:bg-cyan-300"
                />
                <span className="text-[9px] text-slate-500 font-mono mt-1 opacity-80">{pt.time}</span>

                {/* Tooltip */}
                <div className="absolute bottom-full mb-1 hidden group-hover:flex flex-col items-center bg-slate-950 text-white text-[10px] p-1.5 rounded border border-slate-800 shadow-xl z-20 whitespace-nowrap">
                  <span>{pt.time}</span>
                  <span className="font-bold text-cyan-400">{pt.units} units</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart 3: Payment Gateway Success Rate */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5 font-outfit">
            <CreditCard className="w-4 h-4 text-blue-400" /> Gateway Success Rate (%)
          </span>
          <span className="text-[10px] text-slate-500 font-mono">Razorpay / POS</span>
        </div>

        <div className="h-28 flex items-end justify-between gap-1 pt-4 border-b border-slate-800/80 pb-1">
          {points.map((pt, idx) => {
            const heightPct = pt.payment_success_rate;
            const isDegraded = pt.payment_success_rate < 95.0;
            return (
              <div key={idx} className="flex-1 flex flex-col items-center group relative">
                <div
                  style={{ height: `${heightPct}%` }}
                  className={`w-full rounded-t transition-all ${
                    isDegraded ? 'bg-gradient-to-t from-amber-600 to-amber-400' : 'bg-gradient-to-t from-blue-600 to-blue-400'
                  }`}
                />
                <span className="text-[9px] text-slate-500 font-mono mt-1 opacity-80">{pt.time}</span>

                {/* Tooltip */}
                <div className="absolute bottom-full mb-1 hidden group-hover:flex flex-col items-center bg-slate-950 text-white text-[10px] p-1.5 rounded border border-slate-800 shadow-xl z-20 whitespace-nowrap">
                  <span>{pt.time}</span>
                  <span className={`font-bold ${isDegraded ? 'text-amber-400' : 'text-blue-400'}`}>{pt.payment_success_rate}%</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
