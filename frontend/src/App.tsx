import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { SearchBar } from './components/SearchBar';
import { DemoScenarios } from './components/DemoScenarios';
import { StoreCard } from './components/StoreCard';
import { MapView } from './components/MapView';
import { ProductScanModal } from './components/ProductScanModal';
import { MerchantDashboard } from './components/MerchantDashboard';
import { searchLocalProducts, getStoreRoute, checkBackendHealth } from './services/api';
import { SearchResponse, StoreRecommendation, StoreRoute } from './types';
import { Sparkles, MapPin, AlertCircle, Compass } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'merchant' | 'search' | 'scan'>('merchant');
  const [isBackendConnected, setIsBackendConnected] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [searchResult, setSearchResult] = useState<SearchResponse | null>(null);
  const [selectedStore, setSelectedStore] = useState<StoreRecommendation | null>(null);
  const [activeRoute, setActiveRoute] = useState<StoreRoute | null>(null);
  const [activeScenario, setActiveScenario] = useState<string>('rising_demand_stockout');
  const [locationSource, setLocationSource] = useState<string>('Demo Location: New Delhi');

  const [userLocation, setUserLocation] = useState({ latitude: 28.6139, longitude: 77.2090 });

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setUserLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
          setLocationSource('Live GPS Geolocation');
        },
        (err) => setLocationSource('Demo Location: New Delhi'),
        { timeout: 5000 }
      );
    }
    checkBackendHealth().then((res) => {
      setIsBackendConnected(res.status === 'healthy');
    });
    handleSearch("Find fresh Amul milk under 70 rupees within 3 km");
  }, []);

  const handleSearch = async (query: string) => {
    setIsLoading(true);
    try {
      const res = await searchLocalProducts(query, userLocation.latitude, userLocation.longitude);
      setSearchResult(res);
      if (res.recommendations && res.recommendations.length > 0) {
        const best = res.recommendations[0];
        setSelectedStore(best);
        fetchRoute(best.store_id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchRoute = async (storeId: number) => {
    try {
      const route = await getStoreRoute(storeId, userLocation.latitude, userLocation.longitude);
      setActiveRoute(route);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectStore = (store: StoreRecommendation) => {
    setSelectedStore(store);
    fetchRoute(store.store_id);
  };

  const handleSelectScenario = (scenarioId: string) => {
    setActiveScenario(scenarioId);
    if (scenarioId === 'consumer_discovery') {
      setActiveTab('search');
      handleSearch("Find fresh Amul milk under 70 rupees within 3 km");
    } else if (scenarioId === 'stale_inventory') {
      setActiveTab('search');
      handleSearch("Check Amul milk stock at Modern Bazaar");
    } else if (scenarioId === 'ocr_failure') {
      setActiveTab('scan');
    } else {
      setActiveTab('merchant');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} isBackendConnected={isBackendConnected} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Hackathon Preset Scenario Switcher */}
        <DemoScenarios onSelectScenario={handleSelectScenario} activeScenario={activeScenario} />

        {/* MODE 1: MERCHANT INTELLIGENCE DASHBOARD (PRIMARY) */}
        {activeTab === 'merchant' && <MerchantDashboard />}

        {/* MODE 2: CONSUMER LOCAL DISCOVERY */}
        {activeTab === 'search' && (
          <div className="space-y-6">
            
            {/* Location Banner */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-3 px-4 flex items-center justify-between text-xs text-slate-400">
              <span className="flex items-center gap-1.5 font-semibold text-cyan-400">
                <Compass className="w-4 h-4 text-cyan-400" /> Consumer Discovery Mode
              </span>
              <span className="bg-slate-950 px-2.5 py-1 rounded border border-slate-800 font-mono text-[11px]">
                {locationSource} ({userLocation.latitude.toFixed(4)}, {userLocation.longitude.toFixed(4)})
              </span>
            </div>

            {/* Search Input Section */}
            <SearchBar onSearch={handleSearch} isLoading={isLoading} />

            {/* Natural Language Intent Pill */}
            {searchResult && (
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between text-xs gap-3">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-cyan-400 uppercase tracking-wider text-[11px] flex items-center gap-1">
                    <Sparkles className="w-3.5 h-3.5" /> Structured Intent:
                  </span>
                  <span className="bg-slate-950 text-slate-300 px-3 py-1 rounded-lg border border-slate-800 font-mono">
                    Product: <strong>{searchResult.intent.product}</strong> | Max Price: <strong>₹{searchResult.intent.max_price || 'Any'}</strong> | Radius: <strong>{searchResult.intent.radius_km} km</strong>
                  </span>
                </div>

                <div className="text-slate-400 italic">
                  "{searchResult.explanation}"
                </div>
              </div>
            )}

            {/* Split Screen Layout: Stores List (Left) & Leaflet Map (Right) */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
              
              {/* Left Column: Recommended Stores (7 cols) */}
              <div className="lg:col-span-7 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold text-white font-outfit flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-cyan-400" />
                    <span>Nearby Stores & Stock Prediction</span>
                  </h2>
                  <span className="text-xs text-slate-400">
                    {searchResult?.recommendations.length || 0} candidate stores evaluated
                  </span>
                </div>

                {isLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((n) => (
                      <div key={n} className="h-44 bg-slate-900/40 rounded-2xl animate-pulse border border-slate-800/50" />
                    ))}
                  </div>
                ) : searchResult && searchResult.recommendations.length > 0 ? (
                  <div className="space-y-4">
                    {searchResult.recommendations.map((store) => (
                      <StoreCard
                        key={store.store_id}
                        store={store}
                        isSelected={selectedStore?.store_id === store.store_id}
                        onSelect={handleSelectStore}
                        onNavigate={handleSelectStore}
                      />
                    ))}
                  </div>
                ) : (
                  <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 text-center text-slate-400 space-y-2">
                    <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
                    <p className="font-semibold text-slate-200">No stores found matching criteria.</p>
                  </div>
                )}
              </div>

              {/* Right Column: Interactive Leaflet Map (5 cols) */}
              <div className="lg:col-span-5 sticky top-20 h-[600px]">
                <MapView
                  userLocation={userLocation}
                  stores={searchResult?.recommendations || []}
                  selectedStore={selectedStore}
                  activeRoute={activeRoute}
                  onSelectStore={handleSelectStore}
                />
              </div>

            </div>

          </div>
        )}

        {/* MODE 3: PRODUCT VERIFICATION SCANNER */}
        {activeTab === 'scan' && <ProductScanModal />}

      </main>

      {/* Footer Disclaimer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500 font-sans">
        ShopWise AI — Real-Time Commerce Intelligence
      </footer>
    </div>
  );
};
