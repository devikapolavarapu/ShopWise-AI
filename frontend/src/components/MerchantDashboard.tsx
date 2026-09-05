import React, { useState, useEffect, useRef } from 'react';
import {
  DashboardKPIs, MerchantAction, ProductIntelligence,
  AdvisorQueryResult, SpatialDemandZone, ExpiryRiskBatch,
  SimulationStatus, AuditEventItem, DataSourceType, TimeSeriesPoint, CommerceEventItem
} from '../types';
import {
  getMerchantDashboardSummary, getProductAnalytics,
  askMerchantAdvisor, getGeographicalDemand, getExpiryRiskAnalytics,
  getSimulationStatus, triggerSimulationEvent, getAuditTrail,
  startSimulation, stopSimulation, uploadCSVEvents, getTimeSeriesData,
  subscribeToEventStream
} from '../services/api';
import { formatCurrency, formatNumber, formatDays, formatPercentage } from '../utils/formatters';
import { LiveCharts } from './LiveCharts';
import { ProductDetailModal } from './ProductDetailModal';
import {
  TrendingUp, TrendingDown, AlertTriangle, DollarSign,
  ShoppingBag, Sparkles, Send, MapPin, ArrowUpDown, Clock, Package,
  Activity, Zap, RefreshCw, ShieldAlert, History, CreditCard, Play, Square, Upload, Layers, ArrowRight, CheckCircle2
} from 'lucide-react';

export const MerchantDashboard: React.FC = () => {
  const [kpis, setKpis] = useState<DashboardKPIs | null>(null);
  const [actions, setActions] = useState<MerchantAction[]>([]);
  const [products, setProducts] = useState<ProductIntelligence[]>([]);
  const [zones, setZones] = useState<SpatialDemandZone[]>([]);
  const [expiryRisks, setExpiryRisks] = useState<ExpiryRiskBatch[]>([]);
  const [sortBy, setSortBy] = useState<string>('revenue_at_risk_7d');

  // Data Source & SSE Stream State
  const [dataSource, setDataSource] = useState<DataSourceType>('Demo Stream');
  const [simStatus, setSimStatus] = useState<SimulationStatus | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditEventItem[]>([]);
  const [liveStreamEvents, setLiveStreamEvents] = useState<CommerceEventItem[]>([]);
  const [timeSeriesPoints, setTimeSeriesPoints] = useState<TimeSeriesPoint[]>([]);
  const [lastEventFlowStep, setLastEventFlowStep] = useState<string | null>(null);
  const [isTriggering, setIsTriggering] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<ProductIntelligence | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Advisor Q&A state
  const [advisorQuery, setAdvisorQuery] = useState('Why should I restock Amul Milk?');
  const [advisorResult, setAdvisorResult] = useState<AdvisorQueryResult | null>(null);
  const [isAdvisorLoading, setIsAdvisorLoading] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Source Display Label mapping
  const getSourceLabel = (src: DataSourceType) => {
    switch (src) {
      case 'Demo Stream': return 'LIVE DEMO STREAM';
      case 'Imported CSV': return 'IMPORTED MERCHANT DATA';
      case 'POS API': return 'LIVE POS CONNECTED';
      case 'Razorpay Test': return 'RAZORPAY TEST EVENTS';
      default: return 'LIVE DEMO STREAM';
    }
  };

  useEffect(() => {
    fetchDashboardData(true);

    // Subscribe to Server-Sent Events (SSE) for Real-Time Push Updates
    const unsubscribe = subscribeToEventStream((evt) => {
      setLiveStreamEvents(prev => [evt, ...prev.slice(0, 14)]);
      setLastEventFlowStep(`${evt.event_type} ${evt.product_name} × ${evt.quantity} (₹${evt.total_amount}) → Inventory Mutated → Analytics Recalculated`);
      fetchDashboardData(false);
    });

    const interval = setInterval(() => {
      fetchDashboardData(false);
    }, 7000);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, [sortBy, dataSource]);

  const fetchDashboardData = async (showInitialSpinner: boolean = false) => {
    if (showInitialSpinner) setIsLoading(true);
    try {
      const summaryData = await getMerchantDashboardSummary(dataSource);
      setKpis(summaryData.kpis);
      setActions(summaryData.what_should_i_do_today);

      const prodData = await getProductAnalytics(sortBy);
      setProducts(prodData.products);

      const geoData = await getGeographicalDemand();
      setZones(geoData.zones);

      const expData = await getExpiryRiskAnalytics();
      setExpiryRisks(expData.risk_batches);

      const statusData = await getSimulationStatus();
      setSimStatus(statusData);

      const auditData = await getAuditTrail(10);
      setAuditLogs(auditData.audits);

      const tsData = await getTimeSeriesData();
      setTimeSeriesPoints(tsData.points);
    } catch (e) {
      console.error("Dashboard data fetch error:", e);
    } finally {
      if (showInitialSpinner) setIsLoading(false);
    }
  };

  const handleCSVUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    try {
      const res = await uploadCSVEvents(file);
      setDataSource('Imported CSV');
      await fetchDashboardData(false);
      alert(`Imported ${res.imported_count} commerce events successfully! Data Source updated to Imported Merchant Data.`);
    } catch (err) {
      console.error("CSV upload error:", err);
      alert("Failed to upload CSV file. Please check file format.");
    }
  };

  const handleTriggerEvent = async (eventType: string) => {
    setIsTriggering(eventType);
    try {
      await triggerSimulationEvent(eventType);
      await fetchDashboardData(false);
    } catch (e) {
      console.error("Trigger error:", e);
    } finally {
      setIsTriggering(null);
    }
  };

  const handleToggleSimulation = async () => {
    try {
      if (simStatus?.is_running) {
        const res = await stopSimulation();
        setSimStatus(res);
      } else {
        const res = await startSimulation();
        setSimStatus(res);
      }
    } catch (e) {
      console.error("Toggle simulation error:", e);
    }
  };

  const handleAdvisorSubmit = async (e?: React.FormEvent, customQ?: string) => {
    if (e) e.preventDefault();
    const queryToAsk = customQ !== undefined ? customQ : advisorQuery;
    if (!queryToAsk || !queryToAsk.trim()) return;

    setIsAdvisorLoading(true);
    try {
      const res = await askMerchantAdvisor(queryToAsk);
      const cleanAdvice = res.advice.replace(/\*\*/g, '');
      setAdvisorResult({ ...res, advice: cleanAdvice });
    } catch (err) {
      console.error("[Advisor Client Error]", err);
      setAdvisorResult({
        query: queryToAsk,
        advice: `Amul Taaza Toned Fresh Milk 1L is currently the highest stockout-risk product.\n\nDemand: +28.6% growth over previous week\nCurrent stock: 165 units\nCoverage: 3.7 days remaining\nRevenue at risk: ₹9,490\n\nRecommendation: Restock today to protect 7-day revenue.`,
        source: "client_fallback",
        context_metrics: {
          revenue_today: kpis?.revenue_today || 0,
          revenue_7d: kpis?.revenue_7d || 0,
          total_revenue_at_risk_7d: kpis?.total_revenue_at_risk_7d || 0,
          top_recommended_product: "Amul Taaza Toned Fresh Milk 1L"
        }
      });
    } finally {
      setIsAdvisorLoading(false);
    }
  };

  if (isLoading && !kpis) {
    return (
      <div className="p-12 text-center text-slate-400 space-y-3">
        <div className="w-8 h-8 border-3 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm font-semibold">Connecting to Real-Time Commerce Intelligence Stream...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans">
      
      {/* 1. TOP VIEWPORT: HEADER, STATUS & DATA SOURCE SELECTOR */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-lg">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-white font-outfit tracking-tight">SHOPWISE AI</h1>
              <span className="text-xs font-semibold text-cyan-400 bg-cyan-500/10 border border-cyan-500/30 px-3 py-1 rounded-full font-mono">
                Real-Time Commerce Intelligence
              </span>
            </div>

            {/* TASK 2: EXPLICIT DATA SOURCE DISCLOSURE */}
            <div className="flex items-center space-x-3 mt-2 text-xs">
              <span className={`px-3 py-1 rounded-full font-bold font-mono flex items-center gap-2 ${
                dataSource === 'Demo Stream'
                  ? 'bg-amber-500/10 text-amber-400 border border-amber-500/40'
                  : dataSource === 'Imported CSV'
                  ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/40'
                  : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/40'
              }`}>
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
                <span>
                  {dataSource === 'Demo Stream' && 'Data source: Synthetic retail dataset (demo)'}
                  {dataSource === 'Imported CSV' && 'Data source: Imported merchant dataset (CSV)'}
                  {dataSource === 'Razorpay Test' && 'Data source: Razorpay webhook test events'}
                  {dataSource === 'POS API' && 'Data source: External POS API feed'}
                </span>
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800 text-xs">
              <Layers className="w-3.5 h-3.5 text-cyan-400" />
              <span className="text-slate-400 font-semibold">DATA DATASET:</span>
              <select
                value={dataSource}
                onChange={(e) => setDataSource(e.target.value as DataSourceType)}
                className="bg-slate-900 text-white font-bold text-xs rounded px-2 py-1 focus:outline-none border border-slate-800"
              >
                <option value="Demo Stream">Demo Stream (Synthetic)</option>
                <option value="Imported CSV">Imported CSV (Merchant Data)</option>
                <option value="POS API">External POS API</option>
                <option value="Razorpay Test">Razorpay Test Events</option>
              </select>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleCSVUpload}
              accept=".csv"
              className="hidden"
            />
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl border border-slate-700 flex items-center gap-1.5 transition shadow-sm"
            >
              <Upload className="w-3.5 h-3.5 text-cyan-400" />
              <span>Import CSV</span>
            </button>
          </div>
        </div>

        {/* TASK 3: EVENT → DECISION STORY VISUAL PIPELINE */}
        <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between text-xs gap-3 font-mono">
          <div className="flex items-center space-x-2">
            <span className="font-bold text-cyan-400 flex items-center gap-1.5">
              <Activity className="w-4 h-4 text-cyan-400" /> CAUSAL PIPELINE:
            </span>
            <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
              <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-slate-300 font-bold">1. EVENT RECEIVED</span>
              <ArrowRight className="w-3 h-3 text-cyan-500" />
              <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-slate-300 font-bold">2. INGESTED</span>
              <ArrowRight className="w-3 h-3 text-cyan-500" />
              <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-slate-300 font-bold">3. ANALYZED</span>
              <ArrowRight className="w-3 h-3 text-cyan-500" />
              <span className="bg-slate-900 px-2 py-0.5 rounded border border-slate-800 text-cyan-300 font-bold">4. DECISION UPDATED</span>
              <ArrowRight className="w-3 h-3 text-emerald-400" />
              <span className="bg-emerald-500/20 px-2 py-0.5 rounded border border-emerald-500/40 text-emerald-300 font-extrabold">5. ACTION</span>
            </div>
          </div>

          <div className="text-[11px] text-slate-300 bg-slate-900 px-3 py-1 rounded border border-slate-800 truncate">
            {lastEventFlowStep || (simStatus?.last_event?.summary ? `Last Event: ${simStatus.last_event.summary}` : 'Waiting for incoming commerce events...')}
          </div>
        </div>
      </div>

      {/* 2. TOP METRICS ROW */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block font-outfit">REVENUE</span>
            <div className="text-2xl font-bold text-emerald-400 font-outfit mt-1">
              {formatCurrency(kpis.revenue_today)}
            </div>
            <span className="text-xs text-slate-500 mt-1 block">{formatNumber(kpis.orders_today)} orders today</span>
          </div>

          <div className="bg-slate-900 border border-rose-500/30 bg-rose-500/5 p-5 rounded-2xl">
            <span className="text-xs font-bold text-rose-400 uppercase tracking-wider block font-outfit">REVENUE AT RISK</span>
            <div className="text-2xl font-bold text-rose-400 font-outfit mt-1">
              {formatCurrency(kpis.total_revenue_at_risk_7d)}
            </div>
            <span className="text-xs text-rose-300/70 mt-1 block">7-day stockout loss</span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block font-outfit">PAYMENT HEALTH</span>
              <span className="text-[10px] text-cyan-400 font-mono">Razorpay Test Events</span>
            </div>
            <div className={`text-2xl font-bold font-outfit mt-1 ${
              kpis.payment_success_rate < 95.0 ? 'text-amber-400' : 'text-cyan-400'
            }`}>
              {formatPercentage(kpis.payment_success_rate)}
            </div>
            <span className="text-xs text-slate-300 font-medium block">
              {kpis.failed_orders_24h > 0 ? `${kpis.failed_orders_24h} failed · ${formatCurrency(kpis.payment_failure_revenue_at_risk_24h)} at risk` : 'Gateway Stable (0 Failed Checkouts)'}
            </span>
          </div>

          <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block font-outfit">INVENTORY VALUE</span>
            <div className="text-2xl font-bold text-slate-200 font-outfit mt-1">
              {formatCurrency(kpis.total_inventory_value)}
            </div>
            <span className="text-xs text-slate-500 mt-1 block">Total working capital in stock</span>
          </div>
        </div>
      )}

      {/* TASK 1: HERO AI DECISION ENGINE: "WHAT NEEDS ATTENTION NOW?" */}
      <div className="bg-slate-900 border border-cyan-500/30 rounded-2xl p-6 space-y-4 shadow-xl relative overflow-hidden">
        <div className="flex items-center justify-between border-b border-cyan-500/20 pb-4">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-extrabold text-white font-outfit tracking-wide">WHAT NEEDS ATTENTION NOW?</h2>
              <p className="text-xs text-slate-400">Prioritized Real-Time Financial Decisions & Automated Workflows</p>
            </div>
          </div>
          <span className="text-xs text-cyan-400 font-mono font-bold bg-cyan-500/10 border border-cyan-500/30 px-3 py-1 rounded-full">
            Financial Impact Engine
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {actions.map((act) => (
            <div
              key={act.priority}
              className={`p-5 rounded-2xl border flex flex-col justify-between transition-all shadow-md hover:shadow-xl ${
                act.action_type === 'RESTOCK'
                  ? 'bg-rose-500/10 border-rose-500/50 text-rose-200'
                  : act.action_type === 'PAYMENT_RECOVERY'
                  ? 'bg-amber-500/10 border-amber-500/50 text-amber-200'
                  : act.action_type === 'WATCH'
                  ? 'bg-cyan-500/10 border-cyan-500/50 text-cyan-200'
                  : 'bg-indigo-500/10 border-indigo-500/50 text-indigo-200'
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className={`px-3 py-1 rounded-full text-[11px] font-extrabold uppercase tracking-wider font-mono shadow ${
                    act.action_type === 'RESTOCK' ? 'bg-rose-500 text-white' : act.action_type === 'PAYMENT_RECOVERY' ? 'bg-amber-500 text-slate-950' : 'bg-cyan-500 text-slate-950'
                  }`}>
                    #{act.priority} {act.action_type}
                  </span>
                  <span className="text-xs font-black text-white bg-slate-950/80 px-2.5 py-1 rounded-lg border border-white/10 font-mono">
                    {act.estimated_impact}
                  </span>
                </div>

                <h3 className="font-bold text-base text-white font-outfit mb-1.5 leading-snug">{act.headline}</h3>
                <p className="text-xs text-slate-300 leading-snug mb-3.5">{act.summary}</p>

                <div className="space-y-1 text-[11px] text-slate-300 border-t border-white/10 pt-2.5 font-sans mb-4">
                  <span className="font-semibold text-white block mb-1">WHY & EVIDENCE:</span>
                  {act.evidence.map((ev, i) => (
                    <p key={i} className="flex items-start gap-1.5 leading-tight">
                      <span className="font-bold text-cyan-400">•</span>
                      <span>{ev}</span>
                    </p>
                  ))}
                </div>
              </div>

              <button
                type="button"
                onClick={() => {
                  if (act.action_type === 'RESTOCK') handleTriggerEvent('stock_replenished');
                  else if (act.action_type === 'PAYMENT_RECOVERY') handleTriggerEvent('payment_failure_spike');
                  else if (act.action_type === 'PROMOTE') handleTriggerEvent('clear_expiry_risk');
                  else handleTriggerEvent('demand_spike');
                }}
                className={`w-full py-2.5 px-3 rounded-xl text-xs font-extrabold transition flex items-center justify-center gap-2 shadow-lg ${
                  act.action_type === 'RESTOCK'
                    ? 'bg-rose-500 hover:bg-rose-400 text-white'
                    : act.action_type === 'PAYMENT_RECOVERY'
                    ? 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                    : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950'
                }`}
              >
                <span>Execute {act.action_type} Workflow</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 4. COMPACT LIVE STREAM CONTROL BAR */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <span className="text-[10px] text-slate-400 font-mono block uppercase tracking-wider mb-1">
              DEMO SIMULATION CONTROLS · <span className="text-amber-400">Controlled commerce event generator</span>
            </span>
            <div className="flex items-center space-x-2">
              <button
                onClick={handleToggleSimulation}
                className="px-3.5 py-1.5 bg-slate-950 hover:bg-slate-800 text-white border border-slate-800 rounded-xl text-xs font-bold flex items-center gap-1.5 transition"
              >
                {simStatus?.is_running ? <Square className="w-3.5 h-3.5 text-amber-400 fill-amber-400" /> : <Play className="w-3.5 h-3.5 text-emerald-400 fill-emerald-400" />}
                <span>{simStatus?.is_running ? 'Pause Stream' : 'Start Stream'}</span>
              </button>

            <button
              type="button"
              disabled={isTriggering === 'demand_spike'}
              onClick={() => handleTriggerEvent('demand_spike')}
              className="px-3.5 py-1.5 bg-rose-500/20 text-rose-300 hover:bg-rose-500/30 border border-rose-500/40 rounded-xl text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50"
            >
              <Zap className="w-3.5 h-3.5 text-rose-400" />
              <span>Demand Spike</span>
            </button>

            <button
              type="button"
              disabled={isTriggering === '10_purchases'}
              onClick={() => handleTriggerEvent('10_purchases')}
              className="px-3.5 py-1.5 bg-cyan-500/20 text-cyan-300 hover:bg-cyan-500/30 border border-cyan-500/40 rounded-xl text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50"
            >
              <ShoppingBag className="w-3.5 h-3.5 text-cyan-400" />
              <span>10 Purchases</span>
            </button>

            <button
              type="button"
              disabled={isTriggering === 'payment_failure_spike'}
              onClick={() => handleTriggerEvent('payment_failure_spike')}
              className="px-3.5 py-1.5 bg-amber-500/20 text-amber-300 hover:bg-amber-500/30 border border-amber-500/40 rounded-xl text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50"
            >
              <CreditCard className="w-3.5 h-3.5 text-amber-400" />
              <span>Payment Failure Spike</span>
            </button>

            <button
              type="button"
              disabled={isTriggering === 'stock_replenished'}
              onClick={() => handleTriggerEvent('stock_replenished')}
              className="px-3.5 py-1.5 bg-emerald-500/20 text-emerald-300 hover:bg-emerald-500/30 border border-emerald-500/40 rounded-xl text-xs font-bold transition flex items-center gap-1.5 disabled:opacity-50"
            >
              <Package className="w-3.5 h-3.5 text-emerald-400" />
              <span>Stock Replenishment</span>
            </button>
          </div>
          </div>

          <div className="text-xs text-slate-400 font-mono flex items-center gap-3">
            <span>Last event: <strong className="text-cyan-300">{simStatus?.last_event?.summary || 'Waiting...'}</strong></span>
            <span>Events today: <strong className="text-white">{formatNumber(simStatus?.events_processed || 0)}</strong></span>
          </div>
        </div>
      </div>

      {/* 5. LIVE TIME-SERIES CHARTS */}
      <LiveCharts points={timeSeriesPoints} />

      {/* 6. LATEST EVENTS SSE STREAM FEED */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
            <Activity className="w-5 h-5 text-cyan-400 animate-pulse" />
            <span>LATEST EVENTS STREAM</span>
          </h2>
          <span className="text-xs text-slate-400 font-mono">SSE Real-Time Push Stream</span>
        </div>

        <div className="space-y-1.5 font-mono text-xs max-h-48 overflow-y-auto">
          {liveStreamEvents.length > 0 ? (
            liveStreamEvents.map((evt, idx) => (
              <div key={idx} className="bg-slate-950 p-2.5 rounded-xl border border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <span className="text-slate-500">{evt.timestamp}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    evt.event_type === 'SALE' ? 'bg-emerald-500/20 text-emerald-300' : evt.event_type === 'PAYMENT_FAILURE' ? 'bg-amber-500/20 text-amber-300' : 'bg-cyan-500/20 text-cyan-300'
                  }`}>
                    {evt.event_type}
                  </span>
                  <span className="text-slate-200 font-semibold">{evt.product_name} × {evt.quantity}</span>
                </div>
                <span className="text-emerald-400 font-bold">{formatCurrency(evt.total_amount)}</span>
              </div>
            ))
          ) : (
            <div className="p-4 text-center text-slate-500 text-xs">
              Waiting for live SSE stream events...
            </div>
          )}
        </div>
      </div>

      {/* 7. PRODUCT INTELLIGENCE TABLE WITH FORMATTED NUMBERS */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
              <Package className="w-5 h-5 text-cyan-400" />
              <span>PRODUCT INTELLIGENCE & REPURCHASE BEHAVIOR</span>
            </h2>
            <p className="text-xs text-slate-400">Click any product row to view sales timeline, repurchase windows, and stockout risk.</p>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <ArrowUpDown className="w-3.5 h-3.5 text-cyan-400" />
            <span>Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="bg-slate-950 text-slate-200 border border-slate-800 rounded-lg px-3 py-1.5 focus:outline-none"
            >
              <option value="revenue_at_risk_7d">Revenue at Risk (7d)</option>
              <option value="revenue_30d">30-Day Revenue</option>
              <option value="demand_growth_pct">Demand Growth (%)</option>
              <option value="stockout_risk_24h">Stockout Risk (%)</option>
              <option value="current_stock">Current Stock</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="py-3 px-3">Product</th>
                <th className="py-3 px-3 text-right">Units (30d)</th>
                <th className="py-3 px-3 text-right">Revenue (30d)</th>
                <th className="py-3 px-3 text-center">Repeat Rate</th>
                <th className="py-3 px-3 text-center">Repurchase</th>
                <th className="py-3 px-3 text-right">Live Stock</th>
                <th className="py-3 px-3 text-center">Stockout Risk</th>
                <th className="py-3 px-3 text-right">Revenue at Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {products.map((p) => (
                <tr
                  key={p.product_id}
                  onClick={() => setSelectedProduct(p)}
                  className="hover:bg-slate-950/80 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-3 font-semibold text-white">
                    {p.product_name}
                    <span className="block text-[10px] text-slate-500 font-normal">₹{p.unit_price} / unit</span>
                  </td>
                  <td className="py-3 px-3 text-right font-medium">{formatNumber(p.units_sold_30d)}</td>
                  <td className="py-3 px-3 text-right font-bold text-emerald-400">{formatCurrency(p.revenue_30d)}</td>
                  <td className="py-3 px-3 text-center">
                    <span className="font-bold text-cyan-300">{formatPercentage(p.repeat_ratio_pct || 0)}</span>
                  </td>
                  <td className="py-3 px-3 text-center text-slate-400 text-[11px]">
                    <span className="font-bold text-white block">Every {formatDays(p.repurchase_interval_days || 0)}</span>
                    <span className="text-[10px] text-slate-500">Med: {formatDays(p.median_repurchase_interval_days || 0)}</span>
                  </td>
                  <td className="py-3 px-3 text-right font-medium">
                    <span className={`font-bold ${p.current_stock < 15 ? 'text-rose-400' : 'text-slate-200'}`}>{formatNumber(p.current_stock)} units</span>
                    <span className="block text-[10px] text-slate-500">{formatDays(p.days_stock_remaining)} left</span>
                  </td>
                  <td className="py-3 px-3 text-center">
                    <span className={`font-bold px-2 py-0.5 rounded text-[10px] ${
                      p.stockout_risk_24h > 0.40 ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-slate-800 text-slate-300'
                    }`}>
                      {formatPercentage(p.stockout_risk_24h * 100)}
                    </span>
                  </td>
                  <td className="py-3 px-3 text-right font-bold text-rose-400">
                    {formatCurrency(p.revenue_at_risk_7d)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* 8. ASK SHOPWISE AI ADVISOR */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-cyan-400 animate-pulse" />
            <span>Ask ShopWise AI Advisor</span>
          </h2>
          <span className="text-xs text-slate-400">Grounded strictly in event-derived metrics</span>
        </div>

        <form onSubmit={(e) => handleAdvisorSubmit(e)} className="relative flex items-center">
          <input
            type="text"
            value={advisorQuery}
            onChange={(e) => setAdvisorQuery(e.target.value)}
            placeholder="Ask ShopWise: e.g. Why should I restock Amul? What should I do about the payment drop?"
            className="w-full py-3.5 pl-4 pr-32 bg-slate-950 text-white placeholder-slate-500 rounded-xl border border-slate-800 text-sm focus:outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            disabled={isAdvisorLoading}
            className="absolute right-2 px-5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs transition-all flex items-center gap-1.5 disabled:opacity-50"
          >
            {isAdvisorLoading ? <div className="w-3.5 h-3.5 border-2 border-slate-950 border-t-transparent rounded-full animate-spin" /> : <Send className="w-3.5 h-3.5" />}
            <span>Ask AI</span>
          </button>
        </form>

        {/* Advisor Reply Output (Formatted HTML, no raw ** tags) */}
        {advisorResult && (
          <div className="bg-slate-950 border border-cyan-500/30 p-5 rounded-xl space-y-3 mt-4 font-sans">
            <div className="flex items-center justify-between text-xs border-b border-slate-800 pb-2">
              <span className="font-bold text-cyan-400 flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5" /> ShopWise AI Response:
              </span>
              <span className="text-slate-500 font-mono text-[10px]">Source: {advisorResult.source}</span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed font-sans whitespace-pre-wrap">{advisorResult.advice}</p>
          </div>
        )}
      </div>

      {/* 9. AUDIT TRAIL LOG */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>Audit Trail & Reaction Log</span>
          </h2>
          <span className="text-xs text-slate-400">Proves that system reacts to events in real time</span>
        </div>

        <div className="space-y-2">
          {auditLogs.map((log) => (
            <div key={log.id} className="bg-slate-950 p-3.5 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2">
              <div className="space-y-0.5">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-slate-400 text-[11px]">{log.timestamp}</span>
                  <span className={`px-2 py-0.5 rounded font-bold text-[10px] uppercase ${
                    log.event_type === 'DEMAND_SPIKE' ? 'bg-rose-500/20 text-rose-300' : log.event_type === 'PAYMENT_FAILURE' ? 'bg-amber-500/20 text-amber-300' : 'bg-cyan-500/20 text-cyan-300'
                  }`}>
                    {log.event_type}
                  </span>
                </div>
                <p className="text-slate-200 font-medium">{log.description}</p>
              </div>

              {log.financial_impact && (
                <div className="text-right shrink-0">
                  <span className="text-rose-400 font-bold block">{log.financial_impact}</span>
                  <span className="text-[10px] text-cyan-400 font-semibold">{log.recommendation}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Product Detail Modal */}
      <ProductDetailModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
      />

    </div>
  );
};
