from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.services.analytics import analytics_service
from app.services.advisor import merchant_advisor

router = APIRouter(prefix="/api", tags=["Merchant Intelligence"])

@router.get("/dashboard/summary")
def get_merchant_dashboard_summary(
    store_id: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    kpis = analytics_service.get_dashboard_summary(db, store_id=store_id, source=source)
    actions = merchant_advisor.get_what_to_do_today(db, store_id=store_id)
    return {
        "kpis": kpis,
        "what_should_i_do_today": actions
    }

@router.get("/analytics/products")
def get_product_analytics(
    store_id: Optional[int] = Query(None),
    sort_by: str = Query("revenue_at_risk_7d", description="revenue_at_risk_7d, revenue_30d, demand_growth_pct, stockout_risk_24h, current_stock"),
    db: Session = Depends(get_db)
):
    products = analytics_service.get_product_intelligence(db, store_id=store_id)
    
    # Custom sorting
    if sort_by in products[0]:
        products.sort(key=lambda x: x.get(sort_by, 0), reverse=True)

    return {
        "total_count": len(products),
        "sort_by": sort_by,
        "products": products
    }

@router.get("/analytics/demand")
def get_demand_analytics(store_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    products = analytics_service.get_product_intelligence(db, store_id=store_id)
    rising = [p for p in products if p["demand_trend"] == "RISING"]
    declining = [p for p in products if p["demand_trend"] == "DECLINING"]
    stable = [p for p in products if p["demand_trend"] == "STABLE"]

    return {
        "rising_demand_count": len(rising),
        "declining_demand_count": len(declining),
        "stable_demand_count": len(stable),
        "rising_products": rising,
        "declining_products": declining,
        "stable_products": stable
    }

@router.get("/analytics/revenue")
def get_revenue_analytics(store_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    kpis = analytics_service.get_dashboard_summary(db, store_id=store_id)
    products = analytics_service.get_product_intelligence(db, store_id=store_id)
    
    # Category revenue breakdown
    cat_rev = {}
    for p in products:
        cat = p["category"]
        cat_rev[cat] = cat_rev.get(cat, 0.0) + p["revenue_30d"]

    return {
        "revenue_today": kpis["revenue_today"],
        "revenue_7d": kpis["revenue_7d"],
        "revenue_30d": kpis["revenue_30d"],
        "average_order_value": kpis["average_order_value"],
        "revenue_by_category": cat_rev,
        "top_revenue_products": sorted(products, key=lambda x: x["revenue_30d"], reverse=True)[:5]
    }

@router.get("/analytics/inventory-risk")
def get_inventory_risk_analytics(store_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    products = analytics_service.get_product_intelligence(db, store_id=store_id)
    at_risk = [p for p in products if p["stockout_risk_24h"] >= 0.35 or p["days_stock_remaining"] < 2.0]
    return {
        "at_risk_count": len(at_risk),
        "at_risk_products": at_risk
    }

@router.get("/analytics/revenue-risk")
def get_revenue_risk_analytics(store_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    kpis = analytics_service.get_dashboard_summary(db, store_id=store_id)
    products = analytics_service.get_product_intelligence(db, store_id=store_id)
    opps = [p for p in products if p["revenue_opportunity"] > 0]

    return {
        "total_revenue_at_risk_24h": kpis["total_revenue_at_risk_24h"],
        "total_revenue_at_risk_7d": kpis["total_revenue_at_risk_7d"],
        "revenue_opportunities_count": len(opps),
        "revenue_opportunities": opps,
        "high_risk_products": [p for p in products if p["revenue_at_risk_7d"] > 0]
    }

@router.get("/analytics/expiry-risk")
def get_expiry_risk_analytics(store_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    risks = analytics_service.get_expiry_freshness_risks(db, store_id=store_id)
    total_loss = sum(r["potential_financial_loss"] for r in risks)
    return {
        "batches_at_risk_count": len(risks),
        "total_potential_waste_loss": round(total_loss, 2),
        "risk_batches": risks
    }

@router.get("/analytics/geographical-demand")
def get_geographical_demand_analytics(db: Session = Depends(get_db)):
    zones = analytics_service.get_geographical_demand(db)
    return {
        "zones_count": len(zones),
        "zones": zones
    }
