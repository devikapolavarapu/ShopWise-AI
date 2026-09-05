import {
  SearchResponse, ProductScanResponse, StoreRoute,
  DashboardKPIs, MerchantAction, ProductIntelligence,
  AdvisorQueryResult, DemoScenario, ExpiryRiskBatch, SpatialDemandZone,
  SimulationStatus, AuditEventItem, CommerceEventItem, TimeSeriesPoint
} from '../types';

const API_BASE = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000/api';

// CONSUMER & VERIFICATION APIs
export async function searchLocalProducts(query: string, userLat: number = 28.6139, userLon: number = 77.2090): Promise<SearchResponse> {
  const response = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query: query,
      user_latitude: userLat,
      user_longitude: userLon,
    }),
  });

  if (!response.ok) {
    throw new Error(`Search failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getStoreRoute(storeId: number, userLat: number = 28.6139, userLon: number = 77.2090): Promise<StoreRoute> {
  const response = await fetch(`${API_BASE}/stores/${storeId}/route?user_lat=${userLat}&user_lon=${userLon}`);
  if (!response.ok) {
    throw new Error(`Route fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function scanProductImage(samplePreset?: string, imageBase64?: string, targetProductName?: string): Promise<ProductScanResponse> {
  const response = await fetch(`${API_BASE}/product/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      sample_filename: samplePreset,
      image_base64: imageBase64,
      target_product_name: targetProductName,
    }),
  });

  if (!response.ok) {
    throw new Error(`Product scan failed: ${response.statusText}`);
  }

  return response.json();
}

export async function checkBackendHealth(): Promise<{ status: string; groq_configured: boolean }> {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) return res.json();
  } catch (e) {
    console.warn("Backend API offline");
  }
  return { status: "offline", groq_configured: false };
}

// MERCHANT COMMERCE INTELLIGENCE APIs
export async function getMerchantDashboardSummary(source?: string): Promise<{ kpis: DashboardKPIs; what_should_i_do_today: MerchantAction[] }> {
  const srcParam = source === 'Imported CSV' ? 'CSV_IMPORT' : source === 'POS API' ? 'POS_API' : source === 'Razorpay Test' ? 'RAZORPAY' : source === 'Demo Stream' ? 'DEMO_SIMULATOR' : '';
  const url = srcParam ? `${API_BASE}/dashboard/summary?source=${encodeURIComponent(srcParam)}` : `${API_BASE}/dashboard/summary`;
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Dashboard fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getProductAnalytics(sortBy: string = 'revenue_at_risk_7d'): Promise<{ total_count: number; products: ProductIntelligence[] }> {
  const response = await fetch(`${API_BASE}/analytics/products?sort_by=${sortBy}`);
  if (!response.ok) {
    throw new Error(`Product analytics fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getExpiryRiskAnalytics(): Promise<{ batches_at_risk_count: number; total_potential_waste_loss: number; risk_batches: ExpiryRiskBatch[] }> {
  const response = await fetch(`${API_BASE}/analytics/expiry-risk`);
  if (!response.ok) {
    throw new Error(`Expiry risk fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getGeographicalDemand(): Promise<{ zones_count: number; zones: SpatialDemandZone[] }> {
  const response = await fetch(`${API_BASE}/analytics/geographical-demand`);
  if (!response.ok) {
    throw new Error(`Geographical demand fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function askMerchantAdvisor(query: string): Promise<AdvisorQueryResult> {
  const response = await fetch(`${API_BASE}/advisor/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    throw new Error(`Advisor query failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getDemoScenarios(): Promise<{ scenarios_count: number; scenarios: DemoScenario[] }> {
  const response = await fetch(`${API_BASE}/demo/scenarios`);
  if (!response.ok) {
    throw new Error(`Demo scenarios fetch failed: ${response.statusText}`);
  }
  return response.json();
}

// LIVE SIMULATION & SSE EVENT STREAM APIs
export async function getSimulationStatus(): Promise<SimulationStatus> {
  const response = await fetch(`${API_BASE}/simulation/status`);
  if (!response.ok) {
    throw new Error(`Simulation status fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function startSimulation(): Promise<SimulationStatus> {
  const response = await fetch(`${API_BASE}/simulation/start`, { method: 'POST' });
  if (!response.ok) {
    throw new Error(`Start simulation failed: ${response.statusText}`);
  }
  return response.json();
}

export async function stopSimulation(): Promise<SimulationStatus> {
  const response = await fetch(`${API_BASE}/simulation/stop`, { method: 'POST' });
  if (!response.ok) {
    throw new Error(`Stop simulation failed: ${response.statusText}`);
  }
  return response.json();
}

export async function triggerSimulationEvent(eventType: string): Promise<{ message: string; count?: number; demand_multiplier?: number }> {
  const response = await fetch(`${API_BASE}/simulation/trigger-event`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ event_type: eventType }),
  });
  if (!response.ok) {
    throw new Error(`Trigger simulation event failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getAuditTrail(limit: number = 15): Promise<{ count: number; audits: AuditEventItem[] }> {
  const response = await fetch(`${API_BASE}/simulation/audit-trail?limit=${limit}`);
  if (!response.ok) {
    throw new Error(`Audit trail fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export async function uploadCSVEvents(file: File): Promise<{ status: string; imported_count: number; message: string; source: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/events/upload-csv`, {
    method: 'POST',
    body: formData
  });
  if (!response.ok) {
    throw new Error(`CSV upload failed: ${response.statusText}`);
  }
  return response.json();
}

export async function getTimeSeriesData(): Promise<{ points: TimeSeriesPoint[] }> {
  const response = await fetch(`${API_BASE}/events/time-series`);
  if (!response.ok) {
    throw new Error(`Time series fetch failed: ${response.statusText}`);
  }
  return response.json();
}

export function subscribeToEventStream(onEvent: (event: CommerceEventItem) => void, onError?: (err: any) => void): () => void {
  const eventSource = new EventSource(`${API_BASE}/events/stream`);

  eventSource.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      onEvent(data);
    } catch (err) {
      console.error("Failed to parse SSE event data:", err);
    }
  };

  eventSource.onerror = (err) => {
    if (onError) onError(err);
  };

  return () => {
    eventSource.close();
  };
}
