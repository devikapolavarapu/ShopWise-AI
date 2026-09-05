import math
import requests
from typing import Dict, List, Tuple, Optional

# In-memory cache for Nominatim lookups to avoid excessive public API calls
NOMINATIM_CACHE: Dict[str, Tuple[float, float]] = {
    "connaught place": (28.6139, 77.2090),
    "janpath": (28.6250, 77.2180),
    "khan market": (28.6000, 77.2270),
    "paharganj": (28.6410, 77.2120),
}

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def get_coordinates_nominatim(query: str) -> Optional[Tuple[float, float]]:
    """
    Look up coordinates via Nominatim with caching.
    """
    clean_q = query.strip().lower()
    if clean_q in NOMINATIM_CACHE:
        return NOMINATIM_CACHE[clean_q]

    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "ShopWiseAI-HackathonDemo/1.0"}
        params = {"q": query, "format": "json", "limit": 1}
        resp = requests.get(url, headers=headers, params=params, timeout=3)
        if resp.status_code == 200 and resp.json():
            data = resp.json()[0]
            coords = (float(data["lat"]), float(data["lon"]))
            NOMINATIM_CACHE[clean_q] = coords
            return coords
    except Exception as e:
        print(f"[GeoService] Nominatim lookup error: {e}")

    return None

def get_osrm_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict:
    """
    Fetch routing path from OSRM demo server, or return direct line fallback on failure.
    """
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        resp = requests.get(url, timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("routes"):
                route = data["routes"][0]
                return {
                    "distance_km": round(route["distance"] / 1000.0, 2),
                    "duration_minutes": round(route["duration"] / 60.0, 1),
                    "geometry": route["geometry"]["coordinates"], # [[lon, lat], ...]
                    "source": "osrm"
                }
    except Exception as e:
        print(f"[GeoService] OSRM route error, using direct line fallback: {e}")

    # Fallback direct line path
    dist = haversine_distance(start_lat, start_lon, end_lat, end_lon)
    return {
        "distance_km": dist,
        "duration_minutes": round(dist * 3.0, 1), # Approx 20 km/h city driving
        "geometry": [[start_lon, start_lat], [end_lon, end_lat]],
        "source": "haversine_fallback"
    }
