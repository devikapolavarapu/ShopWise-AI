import React, { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import { StoreRecommendation, StoreRoute } from '../types';

// Custom Marker Icons
const userIcon = L.divIcon({
  className: 'custom-user-pin',
  html: `<div class="w-5 h-5 bg-cyan-400 rounded-full border-2 border-white shadow-lg shadow-cyan-400/50 animate-pulse"></div>`,
  iconSize: [20, 20],
  iconAnchor: [10, 10]
});

const getStoreIcon = (isBest: boolean, isSelected: boolean) => {
  const color = isBest ? '#10b981' : isSelected ? '#0284c7' : '#64748b';
  return L.divIcon({
    className: 'custom-store-pin',
    html: `
      <div class="px-2.5 py-1 rounded-full text-xs font-bold text-white shadow-md flex items-center gap-1 border border-white/40" style="background-color: ${color}">
        🏪 ${isBest ? 'BEST' : ''}
      </div>
    `,
    iconSize: [60, 24],
    iconAnchor: [30, 12]
  });
};

interface MapViewProps {
  userLocation: { latitude: number; longitude: number };
  stores: StoreRecommendation[];
  selectedStore: StoreRecommendation | null;
  activeRoute: StoreRoute | null;
  onSelectStore: (store: StoreRecommendation) => void;
}

// Helper component to center map when selected store changes
const MapRecenter: React.FC<{ lat: number; lng: number }> = ({ lat, lng }) => {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lng], 14, { duration: 1.2 });
  }, [lat, lng, map]);
  return null;
};

export const MapView: React.FC<MapViewProps> = ({
  userLocation,
  stores,
  selectedStore,
  activeRoute,
  onSelectStore
}) => {
  const centerLat = selectedStore ? selectedStore.latitude : userLocation.latitude;
  const centerLng = selectedStore ? selectedStore.longitude : userLocation.longitude;

  // Convert route coordinates [[lon, lat], ...] to [[lat, lon], ...] for Leaflet
  const polylineCoords: [number, number][] = activeRoute
    ? activeRoute.route.geometry.map(([lon, lat]) => [lat, lon])
    : selectedStore
    ? [[userLocation.latitude, userLocation.longitude], [selectedStore.latitude, selectedStore.longitude]]
    : [];

  return (
    <div className="w-full h-full min-h-[450px] relative rounded-2xl overflow-hidden border border-slate-800 shadow-2xl">
      <MapContainer
        center={[userLocation.latitude, userLocation.longitude]}
        zoom={13}
        scrollWheelZoom={false}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapRecenter lat={centerLat} lng={centerLng} />

        {/* User Location Marker */}
        <Marker position={[userLocation.latitude, userLocation.longitude]} icon={userIcon}>
          <Popup>
            <div className="text-xs">
              <strong className="text-cyan-400 font-bold block">Your Location</strong>
              <span>Connaught Place, New Delhi</span>
            </div>
          </Popup>
        </Marker>

        {/* Store Markers */}
        {stores.map((store) => {
          const isSelected = selectedStore?.store_id === store.store_id;
          return (
            <Marker
              key={store.store_id}
              position={[store.latitude, store.longitude]}
              icon={getStoreIcon(store.is_best_option, isSelected)}
              eventHandlers={{
                click: () => onSelectStore(store)
              }}
            >
              <Popup>
                <div className="p-1 space-y-1 text-xs">
                  <strong className="font-bold text-white text-sm block">{store.store_name}</strong>
                  <p className="text-slate-300">Price: <span className="text-emerald-400 font-bold">₹{store.price}</span></p>
                  <p className="text-slate-300">Distance: {store.distance_km} km</p>
                  <p className="text-slate-300">Availability: <span className="text-cyan-400 font-bold">{Math.round(store.availability_confidence * 100)}%</span></p>
                </div>
              </Popup>
            </Marker>
          );
        })}

        {/* Route Line */}
        {polylineCoords.length > 0 && (
          <Polyline
            positions={polylineCoords}
            color="#0284c7"
            weight={4}
            opacity={0.8}
            dashArray="8, 8"
          />
        )}
      </MapContainer>

      {/* Floating Map Overlay Info */}
      {selectedStore && (
        <div className="absolute bottom-4 left-4 right-4 bg-slate-900/90 backdrop-blur-md p-3 rounded-xl border border-slate-800 flex items-center justify-between text-xs text-slate-300 z-[1000] shadow-xl">
          <div>
            <span className="text-slate-400 uppercase font-semibold text-[10px] block">Active Destination</span>
            <strong className="text-white text-sm">{selectedStore.store_name}</strong>
          </div>
          {activeRoute && (
            <div className="text-right">
              <span className="text-emerald-400 font-bold block">{activeRoute.route.distance_km} km ({activeRoute.route.duration_minutes} mins)</span>
              <span className="text-[10px] text-slate-400">Via OSRM Navigation</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
