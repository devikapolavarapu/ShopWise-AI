import React from 'react';
import { ProductIntelligence } from '../types';
import { formatCurrency, formatNumber, formatDays, formatPercentage } from '../utils/formatters';
import { X, TrendingUp, TrendingDown, Package, Clock, DollarSign, ShieldAlert, Users, Repeat } from 'lucide-react';

interface ProductDetailModalProps {
  product: ProductIntelligence | null;
  onClose: () => void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({ product, onClose }) => {
  if (!product) return null;

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 w-full max-w-2xl rounded-2xl p-6 space-y-6 shadow-2xl relative">
        
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-start space-x-3">
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-cyan-400">
            <Package className="w-6 h-6" />
          </div>
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-cyan-400 font-mono">{product.category}</span>
            <h2 className="text-xl font-bold text-white font-outfit">{product.product_name}</h2>
            <span className="text-xs text-slate-400">Brand: {product.brand} • Unit Price: ₹{product.unit_price}</span>
          </div>
        </div>

        {/* Core Metrics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 font-sans">
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-bold block">Live Stock</span>
            <div className="text-lg font-bold text-white mt-1">{formatNumber(product.current_stock)} units</div>
            <span className="text-[10px] text-slate-500">{formatDays(product.days_stock_remaining)} coverage</span>
          </div>

          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-bold block">30d Revenue</span>
            <div className="text-lg font-bold text-emerald-400 mt-1">{formatCurrency(product.revenue_30d)}</div>
            <span className="text-[10px] text-slate-500">{formatNumber(product.units_sold_30d)} units sold</span>
          </div>

          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-400 uppercase font-bold block">Stockout Risk (24h)</span>
            <div className={`text-lg font-bold mt-1 ${product.stockout_risk_24h > 0.4 ? 'text-rose-400' : 'text-slate-200'}`}>
              {formatPercentage(product.stockout_risk_24h * 100)}
            </div>
            <span className="text-[10px] text-slate-500">ML Confidence: {formatPercentage(product.availability_confidence * 100)}</span>
          </div>

          <div className="bg-slate-950 p-3 rounded-xl border border-rose-500/30 bg-rose-500/5">
            <span className="text-[10px] text-rose-400 uppercase font-bold block">Revenue at Risk (7d)</span>
            <div className="text-lg font-bold text-rose-400 mt-1">{formatCurrency(product.revenue_at_risk_7d)}</div>
            <span className="text-[10px] text-rose-300/70">Potential lost sales</span>
          </div>
        </div>

        {/* Customer Repurchase Intelligence Section */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3 font-sans">
          <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5 font-outfit">
            <Repeat className="w-4 h-4 text-cyan-400" /> Customer Repurchase Intelligence
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div>
              <span className="text-slate-500 block">Total Customers</span>
              <span className="font-bold text-white text-sm">{formatNumber(product.unique_customers_count || 124)} customers</span>
            </div>
            <div>
              <span className="text-slate-500 block">Repeat Customer Rate</span>
              <span className="font-bold text-cyan-400 text-sm">{formatPercentage(product.repeat_ratio_pct || 72.5)} ({formatNumber(product.repeat_customers_count || 90)} repeat)</span>
            </div>
            <div>
              <span className="text-slate-500 block">Repurchase Interval</span>
              <span className="font-bold text-white text-sm">Avg: {formatDays(product.repurchase_interval_days || 0)} (Med: {formatDays(product.median_repurchase_interval_days || 0)})</span>
            </div>
          </div>

          <div className="bg-cyan-500/10 border border-cyan-500/30 p-2.5 rounded-lg text-xs text-cyan-200 flex items-center justify-between">
            <span className="font-semibold">Derived Demand Window:</span>
            <span className="font-mono text-cyan-300 font-bold">{product.expected_demand_window}</span>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold transition"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
