export interface StructuredIntent {
  product: string;
  category?: string;
  max_price?: number;
  radius_km?: number;
  freshness_priority?: string;
}

export interface ProductOut {
  id: number;
  name: string;
  brand: string;
  category: string;
  package_size?: string;
  price_range?: string;
  image_url?: string;
}

export interface StoreRecommendation {
  store_id: number;
  store_name: string;
  address: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  price: number;
  current_stock: number;
  availability_confidence: number;
  stockout_risk_24h: number;
  last_updated_minutes_ago: number;
  store_reliability: number;
  recommendation_score: number;
  is_best_option: boolean;
  evidence: string[];
  is_data_stale: boolean;
}

export interface SearchResponse {
  query: string;
  intent: StructuredIntent;
  matched_product?: ProductOut;
  recommendations: StoreRecommendation[];
  explanation: string;
  demo_scenario?: string;
}

export interface FreshnessResult {
  manufacturing_date?: string;
  expiry_date?: string;
  total_shelf_life_days?: number;
  remaining_shelf_life_days?: number;
  freshness_percentage: number;
  status: 'FRESH' | 'GOOD' | 'USE_SOON' | 'NEAR_EXPIRY' | 'EXPIRED' | 'INVALID_DATES' | 'MISSING_EXPIRY';
  evidence: string[];
}

export interface ProductScanResponse {
  ocr_text: string;
  detected_brand?: string;
  detected_product_name?: string;
  detected_mfd?: string;
  detected_exp?: string;
  detected_batch?: string;
  ocr_confidence: number;
  cv_match_status: 'Likely Match' | 'Uncertain' | 'Mismatch';
  cv_confidence: number;
  freshness: FreshnessResult;
  evidence: string[];
  error?: string;
}

export interface StoreRoute {
  store_id: number;
  store_name: string;
  destination: { latitude: number; longitude: number };
  origin: { latitude: number; longitude: number };
  route: {
    distance_km: number;
    duration_minutes: number;
    geometry: number[][];
    source: string;
  };
}

// MERCHANT INTELLIGENCE TYPES
export interface DashboardKPIs {
  revenue_today: number;
  orders_today: number;
  units_sold_today: number;
  average_order_value_today: number;

  revenue_7d: number;
  orders_7d: number;
  units_sold_7d: number;
  average_order_value_7d: number;

  revenue_30d: number;
  orders_30d: number;
  units_sold_30d: number;
  average_order_value_30d: number;
  average_order_value: number;

  payment_success_rate: number;
  failed_orders_24h: number;
  payment_failure_revenue_at_risk_24h: number;

  total_inventory_value: number;
  products_at_risk_count: number;
  total_revenue_at_risk_24h: number;
  total_revenue_at_risk_7d: number;
  data_mode: string;
}

export interface MerchantAction {
  priority: number;
  action_type: 'RESTOCK' | 'WATCH' | 'PROMOTE' | 'PROTECT_REVENUE' | 'PAYMENT_RECOVERY';
  product_name: string;
  headline: string;
  summary: string;
  estimated_impact: string;
  evidence: string[];
}

export interface ProductIntelligence {
  product_id: number;
  product_name: string;
  brand: string;
  category: string;
  unit_price: number;
  units_sold_30d: number;
  orders_count_30d: number;
  revenue_30d: number;
  avg_daily_demand: number;
  units_last_7d: number;
  units_prev_7d: number;
  demand_growth_pct: number;
  demand_trend: 'RISING' | 'STABLE' | 'DECLINING';
  repurchase_interval_days?: number;
  median_repurchase_interval_days?: number;
  unique_customers_count?: number;
  repeat_customers_count?: number;
  repeat_ratio_pct?: number;
  expected_demand_window?: string;
  current_stock: number;
  days_stock_remaining: number;
  availability_confidence: number;
  stockout_risk_24h: number;
  potential_lost_units_24h: number;
  revenue_at_risk_24h: number;
  revenue_at_risk_7d: number;
  revenue_opportunity: number;
}

export interface AdvisorQueryResult {
  query: string;
  advice: string;
  source: string;
  context_metrics: {
    revenue_today: number;
    revenue_7d: number;
    total_revenue_at_risk_7d: number;
    top_recommended_product: string;
  };
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  target_tab: 'merchant' | 'discovery' | 'scan';
  recommended_query?: string;
  sample_preset?: string;
}

export interface ExpiryRiskBatch {
  batch_id: number;
  batch_number: string;
  store_name: string;
  product_name: string;
  manufacturing_date: string;
  expiry_date: string;
  remaining_days: number;
  shelf_life_pct: number;
  status: string;
  units_at_risk: number;
  potential_financial_loss: number;
  recommended_action: string;
}

export interface SpatialDemandZone {
  store_id: number;
  store_name: string;
  zone_name: string;
  latitude: number;
  longitude: number;
  total_current_stock: number;
  total_daily_demand: number;
  demand_intensity: 'HIGH' | 'MEDIUM' | 'LOW';
  zone_stockout_risk: 'HIGH' | 'LOW';
}

// SIMULATION & EVENT STREAM TYPES
export type DataSourceType = 'Demo Stream' | 'Imported CSV' | 'POS API' | 'Razorpay Test';

export interface SimulationStatus {
  is_running: boolean;
  interval_seconds: number;
  events_processed: number;
  last_event?: {
    transaction_id: string;
    timestamp: string;
    product_name: string;
    store_name: string;
    quantity: number;
    total_amount: number;
    status: string;
    gateway_status: string;
    payment_method: string;
    summary: string;
  };
  demand_multiplier: number;
  payment_failure_rate_pct: number;
  payment_success_rate_pct: number;
}

export interface AuditEventItem {
  id: number;
  timestamp: string;
  event_type: string;
  description: string;
  metric_changes: Record<string, any>;
  recommendation?: string;
  financial_impact?: string;
}

export interface CommerceEventItem {
  id: number;
  event_id: string;
  event_type: string;
  source: string;
  timestamp: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  total_amount: number;
  payment_status: string;
  summary: string;
}

export interface TimeSeriesPoint {
  time: string;
  revenue: number;
  units: number;
  payment_success_rate: number;
}
