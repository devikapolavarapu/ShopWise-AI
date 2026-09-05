import math
from datetime import datetime, timezone, timedelta, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Transaction, Product, Store, Inventory, ProductBatch
from app.ml.model import predictor

class CommerceAnalyticsService:
    def get_dashboard_summary(self, db: Session, store_id: Optional[int] = None, source: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns high-level KPI dashboard metrics calculated deterministically from transaction data.
        """
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        seven_days_ago = now - timedelta(days=7)
        thirty_days_ago = now - timedelta(days=30)

        # Base transaction query
        q_txn = db.query(Transaction)
        if store_id:
            q_txn = q_txn.filter(Transaction.store_id == store_id)
        if source:
            q_txn = q_txn.filter(Transaction.source == source)

        # 1. Today Metrics
        q_today = q_txn.filter(Transaction.timestamp >= today_start)
        rev_today_res = q_today.with_entities(func.sum(Transaction.total_amount)).scalar()
        revenue_today = float(rev_today_res or 0.0)
        orders_today = q_today.count()
        units_sold_today = int(q_today.with_entities(func.sum(Transaction.quantity)).scalar() or 0)
        aov_today = round(revenue_today / max(1, orders_today), 2) if orders_today > 0 else 0.0

        # 2. 7-Day Metrics
        q_7d = q_txn.filter(Transaction.timestamp >= seven_days_ago)
        rev_7d_res = q_7d.with_entities(func.sum(Transaction.total_amount)).scalar()
        revenue_7d = float(rev_7d_res or 0.0)
        orders_7d = q_7d.count()
        units_sold_7d = int(q_7d.with_entities(func.sum(Transaction.quantity)).scalar() or 0)
        aov_7d = round(revenue_7d / max(1, orders_7d), 2) if orders_7d > 0 else 0.0

        # 3. 30-Day Metrics
        q_30d = q_txn.filter(Transaction.timestamp >= thirty_days_ago)
        rev_30d_res = q_30d.with_entities(func.sum(Transaction.total_amount)).scalar()
        revenue_30d = float(rev_30d_res or 0.0)
        orders_30d = q_30d.count()
        units_sold_30d = int(q_30d.with_entities(func.sum(Transaction.quantity)).scalar() or 0)
        aov_30d = round(revenue_30d / max(1, orders_30d), 2) if orders_30d > 0 else 0.0

        # 4. Payment Gateway & Razorpay Failure Risk Metrics
        q_failed_24h = q_txn.filter(
            Transaction.timestamp >= (now - timedelta(hours=24)),
            Transaction.gateway_status == "FAILED"
        )
        failed_orders_24h = q_failed_24h.count()
        payment_failure_revenue_at_risk_24h = float(q_failed_24h.with_entities(func.sum(Transaction.total_amount)).scalar() or 0.0)

        total_txns_24h = q_txn.filter(Transaction.timestamp >= (now - timedelta(hours=24))).count()
        successful_txns_24h = total_txns_24h - failed_orders_24h
        payment_success_rate = round((successful_txns_24h / max(1, total_txns_24h)) * 100.0, 1)

        # 5. Inventory Valuation
        inv_query = db.query(Inventory)
        if store_id:
            inv_query = inv_query.filter(Inventory.store_id == store_id)
        inventories_all = inv_query.all()
        total_inventory_value = sum(i.current_stock * i.price for i in inventories_all)

        # 6. Products Analytics list
        product_analytics = self.get_product_intelligence(db, store_id=store_id)
        
        # 7. Products at Risk count & Total Revenue at Risk
        products_at_risk_count = sum(1 for p in product_analytics if p["stockout_risk_24h"] > 0.40)
        total_revenue_at_risk_24h = sum(p["revenue_at_risk_24h"] for p in product_analytics)
        total_revenue_at_risk_7d = sum(p["revenue_at_risk_7d"] for p in product_analytics)

        return {
            "revenue_today": round(revenue_today, 2),
            "orders_today": orders_today,
            "units_sold_today": units_sold_today,
            "average_order_value_today": aov_today,

            "revenue_7d": round(revenue_7d, 2),
            "orders_7d": orders_7d,
            "units_sold_7d": units_sold_7d,
            "average_order_value_7d": aov_7d,

            "revenue_30d": round(revenue_30d, 2),
            "orders_30d": orders_30d,
            "units_sold_30d": units_sold_30d,
            "average_order_value_30d": aov_30d,
            "average_order_value": aov_30d,  # fallback alias

            "payment_success_rate": payment_success_rate,
            "failed_orders_24h": failed_orders_24h,
            "payment_failure_revenue_at_risk_24h": round(payment_failure_revenue_at_risk_24h, 2),

            "total_inventory_value": round(total_inventory_value, 2),
            "products_at_risk_count": products_at_risk_count,
            "total_revenue_at_risk_24h": round(total_revenue_at_risk_24h, 2),
            "total_revenue_at_risk_7d": round(total_revenue_at_risk_7d, 2),
            "data_mode": "Demo / Simulated Commerce Dataset"
        }

    def get_product_intelligence(self, db: Session, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculates demand, purchase frequency, stockout risk, and revenue-at-risk per product.
        """
        now = datetime.utcnow()
        last_7d_start = now - timedelta(days=7)
        prev_7d_start = now - timedelta(days=14)
        last_30d_start = now - timedelta(days=30)

        products = db.query(Product).all()
        results = []

        for p in products:
            # Query transactions for product
            q_p_txn = db.query(Transaction).filter(Transaction.product_id == p.id)
            if store_id:
                q_p_txn = q_p_txn.filter(Transaction.store_id == store_id)

            # 30-day Totals
            txns_30d = q_p_txn.filter(Transaction.timestamp >= last_30d_start).all()
            units_30d = sum(t.quantity for t in txns_30d)
            rev_30d = sum(t.total_amount for t in txns_30d)
            orders_30d = len(txns_30d)

            # Average daily demand
            avg_daily_demand = round(units_30d / 30.0, 1) if units_30d > 0 else 5.0

            # Demand trend: Last 7d vs Prev 7d
            units_last_7d = sum(t.quantity for t in txns_30d if t.timestamp >= last_7d_start)
            units_prev_7d = sum(t.quantity for t in txns_30d if prev_7d_start <= t.timestamp < last_7d_start)

            if units_prev_7d > 0:
                growth_pct = round(((units_last_7d - units_prev_7d) / float(units_prev_7d)) * 100.0, 1)
            else:
                growth_pct = 0.0

            if growth_pct >= 10.0:
                trend = "RISING"
            elif growth_pct <= -10.0:
                trend = "DECLINING"
            else:
                trend = "STABLE"

            # Purchase Frequency & Repurchase Intelligence
            repurchase_info = self._calculate_repurchase_frequency(txns_30d)

            # Current Inventory & Price
            inv_query = db.query(Inventory).filter(Inventory.product_id == p.id)
            if store_id:
                inv_query = inv_query.filter(Inventory.store_id == store_id)
            inventories = inv_query.all()

            current_stock = sum(i.current_stock for i in inventories)
            unit_price = inventories[0].price if inventories else 50.0
            reliability = inventories[0].store.reliability_score if inventories else 0.95

            # ML Stockout Risk Prediction
            avail_conf, stockout_risk_24h = predictor.predict_availability(
                current_stock=current_stock,
                daily_sales_average=avg_daily_demand,
                recent_sales=round(units_last_7d / 7.0, 1),
                store_reliability=reliability
            )

            # Inventory Coverage Days
            days_stock_remaining = round(current_stock / max(0.1, avg_daily_demand), 1)

            # Revenue at Risk (Financial Impact)
            potential_lost_units_24h = max(0, int(avg_daily_demand - current_stock))
            revenue_at_risk_24h = round(potential_lost_units_24h * unit_price, 2)

            # 7-day revenue at risk if demand outpaces stock
            demand_7d = int(avg_daily_demand * 7)
            potential_lost_units_7d = max(0, demand_7d - current_stock)
            revenue_at_risk_7d = round(potential_lost_units_7d * unit_price, 2)

            # Revenue Opportunity protected if restocked
            revenue_opportunity = 0.0
            if trend == "RISING" and days_stock_remaining < 2.0:
                revenue_opportunity = round(potential_lost_units_7d * unit_price * 1.1, 2)

            results.append({
                "product_id": p.id,
                "product_name": p.name,
                "brand": p.brand,
                "category": p.category,
                "unit_price": unit_price,
                "units_sold_30d": units_30d,
                "orders_count_30d": orders_30d,
                "revenue_30d": round(rev_30d, 2),
                "avg_daily_demand": avg_daily_demand,
                "units_last_7d": units_last_7d,
                "units_prev_7d": units_prev_7d,
                "demand_growth_pct": growth_pct,
                "demand_trend": trend,
                "repurchase_interval_days": repurchase_info["repurchase_interval_days"],
                "median_repurchase_interval_days": repurchase_info.get("median_repurchase_interval_days", 4.5),
                "unique_customers_count": repurchase_info["unique_customers_count"],
                "repeat_customers_count": repurchase_info["repeat_customers_count"],
                "repeat_ratio_pct": repurchase_info["repeat_ratio_pct"],
                "expected_demand_window": repurchase_info.get("expected_demand_window", "High probability of repeat demand within 24–48h"),
                "current_stock": current_stock,
                "days_stock_remaining": days_stock_remaining,
                "availability_confidence": avail_conf,
                "stockout_risk_24h": stockout_risk_24h,
                "potential_lost_units_24h": potential_lost_units_24h,
                "revenue_at_risk_24h": revenue_at_risk_24h,
                "revenue_at_risk_7d": revenue_at_risk_7d,
                "revenue_opportunity": revenue_opportunity
            })

        # Sort by revenue_at_risk_7d descending
        results.sort(key=lambda x: x["revenue_at_risk_7d"], reverse=True)
        return results

    def _calculate_repurchase_frequency(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Calculates customer repurchase intelligence metrics using transaction timestamp deltas.
        """
        cust_txns: Dict[str, List[datetime]] = {}
        for t in transactions:
            if t.customer_id not in cust_txns:
                cust_txns[t.customer_id] = []
            cust_txns[t.customer_id].append(t.timestamp)

        unique_customers = len(cust_txns)
        repeat_customers = sum(1 for c, ts in cust_txns.items() if len(ts) >= 2)
        repeat_ratio = round((repeat_customers / max(1, unique_customers)) * 100.0, 1)

        deltas_days = []
        for cust_id, timestamps in cust_txns.items():
            if len(timestamps) >= 2:
                timestamps.sort()
                for i in range(1, len(timestamps)):
                    diff_days = (timestamps[i] - timestamps[i-1]).total_seconds() / 86400.0
                    if diff_days > 0.2: # filter out multiple items in same checkout
                        deltas_days.append(diff_days)

        avg_interval = round(sum(deltas_days) / len(deltas_days), 1) if len(deltas_days) >= 2 else 5.8
        
        # Calculate median repurchase interval
        if deltas_days:
            sorted_deltas = sorted(deltas_days)
            mid = len(sorted_deltas) // 2
            median_interval = round(sorted_deltas[mid], 1)
        else:
            median_interval = 4.5

        if avg_interval <= 3.5:
            demand_window = "High probability of repeat demand within 24–48h"
        elif avg_interval <= 7.0:
            demand_window = "Moderate repeat demand expected within 3–5 days"
        else:
            demand_window = "Periodic repeat purchase pattern (7–14 days)"

        return {
            "repurchase_interval_days": avg_interval,
            "median_repurchase_interval_days": median_interval,
            "unique_customers_count": unique_customers,
            "repeat_customers_count": repeat_customers,
            "repeat_ratio_pct": repeat_ratio,
            "expected_demand_window": demand_window
        }

    def get_expiry_freshness_risks(self, db: Session, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Calculates financial risk from inventory batches approaching expiry (<10% shelf life).
        """
        today = date.today()
        q_batches = db.query(ProductBatch)
        if store_id:
            q_batches = q_batches.filter(ProductBatch.store_id == store_id)

        batches = q_batches.all()
        risk_batches = []

        for b in batches:
            total_days = max(1, (b.expiry_date - b.manufacturing_date).days)
            remaining_days = (b.expiry_date - today).days
            pct_remaining = (remaining_days / total_days) * 100.0

            if pct_remaining < 25.0 or remaining_days <= 2:
                product = b.product
                store = b.store
                inv = db.query(Inventory).filter(
                    Inventory.store_id == b.store_id,
                    Inventory.product_id == b.product_id
                ).first()

                units = inv.current_stock if inv else 10
                price = inv.price if inv else 50.0
                potential_loss = round(units * price, 2)

                action = "PRIORITIZE_SALE"
                if remaining_days <= 0:
                    status = "EXPIRED"
                    action = "DISCARD"
                elif pct_remaining < 10.0:
                    status = "NEAR_EXPIRY"
                    action = "PROMOTE_PROMPTLY"
                else:
                    status = "USE_SOON"
                    action = "MONITOR_OR_MOVE"

                risk_batches.append({
                    "batch_id": b.id,
                    "batch_number": b.batch_number,
                    "store_name": store.name,
                    "product_name": product.name,
                    "manufacturing_date": b.manufacturing_date.strftime("%Y-%m-%d"),
                    "expiry_date": b.expiry_date.strftime("%Y-%m-%d"),
                    "remaining_days": remaining_days,
                    "shelf_life_pct": round(pct_remaining, 1),
                    "status": status,
                    "units_at_risk": units,
                    "potential_financial_loss": potential_loss,
                    "recommended_action": action
                })

        return risk_batches

    def get_geographical_demand(self, db: Session) -> List[Dict[str, Any]]:
        """
        Aggregates demand and store coverage by city zone.
        """
        stores = db.query(Store).all()
        zones = []

        for s in stores:
            invs = db.query(Inventory).filter(Inventory.store_id == s.id).all()
            total_stock = sum(i.current_stock for i in invs)
            daily_demand = sum(i.daily_sales_average for i in invs)
            
            # Demand intensity
            intensity = "HIGH" if daily_demand > 100 else "MEDIUM"
            stockout_risk = "HIGH" if total_stock < daily_demand * 1.2 else "LOW"

            zones.append({
                "store_id": s.id,
                "store_name": s.name,
                "zone_name": s.address.split(",")[0],
                "latitude": s.latitude,
                "longitude": s.longitude,
                "total_current_stock": total_stock,
                "total_daily_demand": round(daily_demand, 1),
                "demand_intensity": intensity,
                "zone_stockout_risk": stockout_risk
            })

        return zones

analytics_service = CommerceAnalyticsService()
