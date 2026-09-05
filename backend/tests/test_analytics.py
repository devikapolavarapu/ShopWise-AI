import pytest
from app.database import SessionLocal
from app.models import Transaction, Inventory
from app.services.analytics import analytics_service

def test_transaction_data_consistency():
    db = SessionLocal()
    try:
        txns = db.query(Transaction).limit(50).all()
        assert len(txns) > 0, "Database should contain seeded transactions"
        for t in txns:
            # Verify total_amount = quantity * unit_price
            expected_total = round(t.quantity * t.unit_price, 2)
            assert abs(t.total_amount - expected_total) < 0.01
    finally:
        db.close()

def test_dashboard_summary_metrics():
    db = SessionLocal()
    try:
        summary = analytics_service.get_dashboard_summary(db)
        assert summary["revenue_30d"] > 0
        assert summary["orders_30d"] > 0
        assert summary["units_sold_30d"] > 0
        assert summary["average_order_value"] > 0
        assert summary["total_revenue_at_risk_7d"] >= 0
    finally:
        db.close()

def test_product_intelligence_demand_trends():
    db = SessionLocal()
    try:
        products = analytics_service.get_product_intelligence(db)
        assert len(products) > 0
        for p in products:
            assert "demand_trend" in p
            assert p["demand_trend"] in ["RISING", "STABLE", "DECLINING"]
            assert p["days_stock_remaining"] >= 0
            assert p["revenue_at_risk_7d"] >= 0
    finally:
        db.close()

def test_repurchase_frequency_calculation():
    db = SessionLocal()
    try:
        products = analytics_service.get_product_intelligence(db)
        # Amul Milk should have repurchase frequency calculated
        milk_prod = next((p for p in products if "Milk" in p["product_name"]), None)
        assert milk_prod is not None
        assert milk_prod["repurchase_interval_days"] is not None
        assert milk_prod["repurchase_interval_days"] > 0
    finally:
        db.close()
