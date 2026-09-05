from app.services.geo import haversine_distance, get_osrm_route

def test_haversine_distance_calculation():
    # CP to Janpath (approx 0.8 - 1.2 km)
    dist = haversine_distance(28.6139, 77.2090, 28.6250, 77.2180)
    assert 0.5 <= dist <= 2.0

def test_osrm_route_fallback():
    # Route calculation should return geometry coordinates
    route = get_osrm_route(28.6139, 77.2090, 28.6250, 77.2180)
    assert "geometry" in route
    assert len(route["geometry"]) >= 2
    assert route["distance_km"] > 0
