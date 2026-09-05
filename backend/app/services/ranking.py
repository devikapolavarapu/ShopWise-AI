from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from app.schemas.entities import StoreRecommendation

class StoreRankingEngine:
    def __init__(
        self,
        weight_distance: float = 0.25,
        weight_availability: float = 0.35,
        weight_price: float = 0.15,
        weight_reliability: float = 0.15,
        weight_freshness: float = 0.10
    ):
        self.w_dist = weight_distance
        self.w_avail = weight_availability
        self.w_price = weight_price
        self.w_rel = weight_reliability
        self.w_fresh = weight_freshness

    def rank_stores(
        self,
        candidate_stores: List[Dict[str, Any]],
        max_radius_km: float = 5.0,
        max_budget: float = None,
        freshness_priority: str = "medium"
    ) -> List[StoreRecommendation]:
        """
        Ranks candidate stores using deterministic multi-criteria scoring.
        """
        if not candidate_stores:
            return []

        # Find min/max for normalization
        max_dist = max([s["distance_km"] for s in candidate_stores] + [max_radius_km, 1.0])
        all_prices = [s["price"] for s in candidate_stores]
        min_price = min(all_prices) if all_prices else 1.0
        max_price_val = max(all_prices) if all_prices else 100.0

        recommendations: List[StoreRecommendation] = []
        now = datetime.utcnow()

        for s in candidate_stores:
            dist_km = s["distance_km"]
            current_stock = s["current_stock"]
            avail_conf = s["availability_confidence"]
            stockout_risk = s["stockout_risk_24h"]
            price = s["price"]
            reliability = s["store_reliability"]
            last_updated = s["last_updated"]
            if last_updated and getattr(last_updated, 'tzinfo', None) is not None:
                last_updated = last_updated.replace(tzinfo=None)

            # Minutes since inventory update
            minutes_ago = max(0.0, (now - last_updated).total_seconds() / 60.0)
            is_stale = minutes_ago > 360 # Stale if > 6 hours old

            # If inventory data is stale, apply confidence penalty
            if is_stale:
                avail_conf = round(max(0.30, avail_conf * 0.70), 2)

            # 1. Distance Score (1.0 = closest, 0.0 = at radius limit)
            s_dist = max(0.0, 1.0 - (dist_km / max_dist))

            # 2. Availability Score (direct model confidence)
            s_avail = avail_conf

            # 3. Price Score (1.0 = cheapest, 0.0 = most expensive)
            if max_price_val > min_price:
                s_price = 1.0 - ((price - min_price) / (max_price_val - min_price))
            else:
                s_price = 1.0

            # Price penalty if exceeds user max_budget
            if max_budget and price > max_budget:
                s_price *= 0.5

            # 4. Store Reliability Score
            s_rel = reliability

            # 5. Freshness Preference Score
            s_fresh = 0.90 if freshness_priority == "high" else 0.75

            # Weighted overall score (0 to 100)
            total_score = (
                self.w_dist * s_dist +
                self.w_avail * s_avail +
                self.w_price * s_price +
                self.w_rel * s_rel +
                self.w_fresh * s_fresh
            ) * 100.0

            evidence = [
                f"{dist_km:.1f} km away from your location",
                f"{int(avail_conf * 100)}% inventory availability confidence",
                f"Predicted stockout risk in 24h: {int(stockout_risk * 100)}%",
                f"Price: ₹{price:.0f}",
                f"Store reliability rating: {int(reliability * 100)}%"
            ]

            if is_stale:
                evidence.append(f"⚠️ Inventory last updated {int(minutes_ago / 60)}h ago (confidence reduced due to stale data)")
            else:
                evidence.append(f"Inventory updated {int(minutes_ago)} min ago")

            rec = StoreRecommendation(
                store_id=s["store_id"],
                store_name=s["store_name"],
                address=s["address"],
                latitude=s["latitude"],
                longitude=s["longitude"],
                distance_km=dist_km,
                price=price,
                current_stock=current_stock,
                availability_confidence=avail_conf,
                stockout_risk_24h=stockout_risk,
                last_updated_minutes_ago=round(minutes_ago, 1),
                store_reliability=reliability,
                recommendation_score=round(total_score, 1),
                is_best_option=False,
                evidence=evidence,
                is_data_stale=is_stale
            )
            recommendations.append(rec)

        # Sort recommendations by recommendation_score descending
        recommendations.sort(key=lambda x: x.recommendation_score, reverse=True)

        if recommendations:
            recommendations[0].is_best_option = True

        return recommendations

ranking_engine = StoreRankingEngine()
