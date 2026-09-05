import React from 'react';
import { StoreRecommendation } from '../types';
import { MapPin, Navigation, ShieldCheck, AlertTriangle, Star, Clock, Tag } from 'lucide-react';

interface StoreCardProps {
  store: StoreRecommendation;
  isSelected: boolean;
  onSelect: (store: StoreRecommendation) => void;
  onNavigate: (store: StoreRecommendation) => void;
}

export const StoreCard: React.FC<StoreCardProps> = ({ store, isSelected, onSelect, onNavigate }) => {
  const stockoutRiskPct = Math.round(store.stockout_risk_24h * 100);
  const availConfPct = Math.round(store.availability_confidence * 100);

  return (
    <div
      onClick={() => onSelect(store)}
      className={`p-5 rounded-2xl border transition-all cursor-pointer relative overflow-hidden ${
        isSelected
          ? 'bg-slate-900 border-cyan-500 shadow-xl shadow-cyan-950/30 ring-1 ring-cyan-500'
          : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
      }`}
    >
      {/* Best Option Pill */}
      {store.is_best_option && (
        <div className="absolute top-0 right-0 bg-gradient-to-l from-emerald-500 to-teal-600 text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider flex items-center gap-1 shadow-md">
          <Star className="w-3 h-3 fill-white" /> ShopWise Recommended
        </div>
      )}

      {/* Header Info */}
      <div className="flex items-start justify-between pr-24">
        <div>
          <h3 className="font-bold text-lg text-white font-outfit leading-snug">{store.store_name}</h3>
          <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
            <MapPin className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
            <span>{store.address}</span> • <strong className="text-cyan-300">{store.distance_km} km away</strong>
          </p>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-3 gap-2 my-4 p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 text-center">
        <div>
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Price</span>
          <span className="text-base font-bold text-emerald-400 flex items-center justify-center gap-0.5">
            <Tag className="w-3.5 h-3.5" /> ₹{store.price}
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">Availability</span>
          <span className="text-base font-bold text-cyan-400 flex items-center justify-center gap-1">
            <ShieldCheck className="w-3.5 h-3.5" /> {availConfPct}%
          </span>
        </div>

        <div>
          <span className="text-[10px] text-slate-400 uppercase font-semibold block">24h Stockout Risk</span>
          <span className={`text-base font-bold flex items-center justify-center gap-1 ${
            stockoutRiskPct > 35 ? 'text-rose-400' : 'text-slate-300'
          }`}>
            {stockoutRiskPct > 35 && <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />}
            {stockoutRiskPct}%
          </span>
        </div>
      </div>

      {/* Score and Stale Warning */}
      <div className="flex items-center justify-between mb-3 text-xs">
        <div className="flex items-center space-x-2">
          <span className="font-semibold text-slate-300">Recommendation Score:</span>
          <span className="px-2.5 py-0.5 rounded-full font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
            {store.recommendation_score} / 100
          </span>
        </div>

        {store.is_data_stale && (
          <span className="text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded text-[11px] font-medium border border-amber-500/20 flex items-center gap-1">
            <Clock className="w-3 h-3" /> Stale Inventory
          </span>
        )}
      </div>

      {/* Evidence List */}
      <div className="space-y-1 text-xs text-slate-400 mb-4 border-t border-slate-800/60 pt-3">
        <span className="font-semibold text-slate-300 block mb-1">Evidence Behind Decision:</span>
        {store.evidence.map((ev, idx) => (
          <p key={idx} className="flex items-start gap-1.5 leading-snug">
            <span className="text-cyan-400 font-bold">•</span>
            <span>{ev}</span>
          </p>
        ))}
      </div>

      {/* Action Button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onNavigate(store);
        }}
        className={`w-full py-2.5 px-4 rounded-xl font-semibold text-sm flex items-center justify-center space-x-2 transition-all ${
          isSelected
            ? 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold shadow-lg shadow-cyan-500/20'
            : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
        }`}
      >
        <Navigation className="w-4 h-4" />
        <span>NAVIGATE TO STORE</span>
      </button>
    </div>
  );
};
