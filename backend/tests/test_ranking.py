from datetime import datetime, timezone, timedelta
from app.services.ranking import StoreRankingEngine

def test_store_ranking_order():
    engine = StoreRankingEngine()
    now = datetime.now(timezone.utc)

    candidate_stores = [
        {
            "store_id": 1,
            "store_name": "Store A (Close & High Stock)",
            "address": "CP Outer Circle",
            "latitude": 28.6328,
            "longitude": 77.2197,
            "distance_km": 0.8,
            "price": 65.0,
            "current_stock": 30,
            "availability_confidence": 0.96,
            "stockout_risk_24h": 0.05,
            "last_updated": now - timedelta(minutes=15),
            "store_reliability": 0.98
        },
        {
            "store_id": 2,
            "store_name": "Store B (Far & Low Stock)",
            "address": "Paharganj",
            "latitude": 28.6410,
            "longitude": 77.2120,
            "distance_km": 3.5,
            "price": 70.0,
            "current_stock": 2,
            "availability_confidence": 0.40,
            "stockout_risk_24h": 0.70,
            "last_updated": now - timedelta(hours=8),
            "store_reliability": 0.80
        }
    ]

    recs = engine.rank_stores(candidate_stores, max_radius_km=5.0)
    assert len(recs) == 2
    assert recs[0].store_id == 1
    assert recs[0].is_best_option is True
    assert recs[0].recommendation_score > recs[1].recommendation_score
    assert recs[1].is_data_stale is True
