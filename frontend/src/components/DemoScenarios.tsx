import React, { useState } from 'react';
import { PlayCircle, ShieldAlert, Clock, AlertTriangle, CheckCircle2, TrendingUp, DollarSign, MapPin, Search, Bot, ChevronDown, ChevronRight } from 'lucide-react';

interface DemoScenariosProps {
  onSelectScenario: (scenarioId: string) => void;
  activeScenario: string;
}

export const DemoScenarios: React.FC<DemoScenariosProps> = ({ onSelectScenario, activeScenario }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const scenarios = [
    {
      id: 'rising_demand_stockout',
      title: '1. Rising Demand Risk',
      desc: 'Amul Milk demand +18% while stock <1 day (₹300 risk)',
      icon: TrendingUp,
      color: 'text-rose-400 border-rose-500/40 bg-rose-500/10'
    },
    {
      id: 'revenue_at_risk',
      title: '2. Revenue at Risk',
      desc: 'Quantifies 7-day lost sales from inventory stockouts',
      icon: DollarSign,
      color: 'text-amber-400 border-amber-500/40 bg-amber-500/10'
    },
    {
      id: 'declining_product',
      title: '3. Declining Demand',
      desc: 'Identifies products losing demand (-15% growth)',
      icon: AlertTriangle,
      color: 'text-orange-400 border-orange-500/40 bg-orange-500/10'
    },
    {
      id: 'high_inventory_low_demand',
      title: '4. High Stock Clearance',
      desc: 'Atta overstocked (85 units) -> Recommend promotion',
      icon: CheckCircle2,
      color: 'text-cyan-400 border-cyan-500/40 bg-cyan-500/10'
    },
    {
      id: 'expiry_risk',
      title: '5. Expiry Financial Risk',
      desc: 'Bread batch has <10% shelf life -> Prioritize sale',
      icon: Clock,
      color: 'text-purple-400 border-purple-500/40 bg-purple-500/10'
    },
    {
      id: 'geographical_demand',
      title: '6. Spatial Demand',
      desc: 'Khan Market high spatial demand cluster',
      icon: MapPin,
      color: 'text-blue-400 border-blue-500/40 bg-blue-500/10'
    },
    {
      id: 'consumer_discovery',
      title: '7. Consumer Discovery',
      desc: 'Search fresh milk < ₹70 within 3km -> Store A',
      icon: Search,
      color: 'text-emerald-400 border-emerald-500/40 bg-emerald-500/10'
    },
    {
      id: 'ocr_failure',
      title: '8. OCR Failure Retake',
      desc: 'Blurry label -> Prompt user to retake image',
      icon: Clock,
      color: 'text-slate-400 border-slate-700 bg-slate-900'
    },
    {
      id: 'stale_inventory',
      title: '9. Stale Inventory',
      desc: 'Data updated 9.5h ago -> 30% confidence penalty',
      icon: ShieldAlert,
      color: 'text-amber-300 border-amber-500/40 bg-amber-500/10'
    },
    {
      id: 'llm_fallback',
      title: '10. Groq LLM Fallback',
      desc: 'API key offline -> Regex parser extracts intent',
      icon: Bot,
      color: 'text-indigo-400 border-indigo-500/40 bg-indigo-500/10'
    }
  ];

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 space-y-3">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between cursor-pointer select-none"
      >
        <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-slate-300 hover:text-white font-outfit">
          <button className="px-2.5 py-1 bg-slate-950 hover:bg-slate-800 text-slate-300 border border-slate-800 rounded-lg text-xs font-bold font-mono flex items-center gap-1.5 transition">
            {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-cyan-400" /> : <ChevronRight className="w-3.5 h-3.5 text-cyan-400" />}
            <span>DEMO SCENARIOS</span>
            <span className="text-[10px] text-slate-500 font-sans font-normal">{isExpanded ? '▾' : '▸'}</span>
          </button>
          <span className="text-slate-400 font-normal font-sans text-xs hidden sm:inline">
            Controlled commerce event generator
          </span>
        </div>

        <span className="text-[11px] text-slate-400 font-mono">
          {isExpanded ? 'Click to collapse' : 'Click to expand 10 test scenarios'}
        </span>
      </div>

      {isExpanded && (
        <div className="grid grid-cols-2 sm:grid-cols-5 lg:grid-cols-10 gap-2 pt-2 border-t border-slate-800/80">
          {scenarios.map((sc) => {
            const Icon = sc.icon;
            const isActive = activeScenario === sc.id;
            return (
              <button
                key={sc.id}
                onClick={() => onSelectScenario(sc.id)}
                className={`p-2 rounded-lg border text-left transition-all flex flex-col justify-between ${
                  isActive
                    ? `${sc.color} ring-2 ring-cyan-500 shadow-md`
                    : 'bg-slate-950/70 border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center space-x-1 font-bold text-[11px] mb-1">
                    <Icon className="w-3 h-3 shrink-0" />
                    <span className="truncate">{sc.title.split('.')[1]}</span>
                  </div>
                  <p className="text-[10px] text-slate-400 line-clamp-2 leading-tight">{sc.desc}</p>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};
