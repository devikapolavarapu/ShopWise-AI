from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Store, Inventory
from app.schemas.entities import SearchRequest, SearchResponse, ProductOut, StructuredIntent
from app.services.llm import llm_service
from app.services.geo import haversine_distance
from app.services.ranking import ranking_engine
from app.ml.model import predictor

router = APIRouter(prefix="/api", tags=["Search"])

@router.post("/search", response_model=SearchResponse)
def search_local_products(request: SearchRequest, db: Session = Depends(get_db)):
    user_lat = request.user_latitude
    user_lon = request.user_longitude

    # Step 1: Extract Intent if query provided, else use explicit fields
    if request.query:
        intent_resp = llm_service.parse_intent(request.query)
        intent = intent_resp.intent
    else:
        intent = StructuredIntent(
            product=request.product_name or "Amul Milk",
            category=request.category or "Dairy",
            max_price=request.max_price,
            radius_km=request.radius_km or 5.0,
            freshness_priority=request.freshness_priority or "medium"
        )

    # Step 2: Match Product in DB
    search_term = intent.product.strip()
    product_obj = db.query(Product).filter(Product.name.ilike(f"%{search_term.split()[0]}%")).first()
    
    if not product_obj:
        product_obj = db.query(Product).filter(Product.category.ilike(f"%{intent.category}%")).first()

    if not product_obj:
        product_obj = db.query(Product).first()

    matched_p_out = ProductOut.from_orm(product_obj) if product_obj else None

    # Step 3: Find Candidate Stores and Inventory
    inventories = db.query(Inventory).filter(Inventory.product_id == product_obj.id).all() if product_obj else []

    candidate_stores = []
    for inv in inventories:
        store = inv.store
        dist_km = haversine_distance(user_lat, user_lon, store.latitude, store.longitude)

        # Check distance limit
        if dist_km > (intent.radius_km * 1.5): # Generous cutoff for ranking
            continue

        # Predict stockout risk using ML model
        avail_conf, stockout_risk = predictor.predict_availability(
            current_stock=inv.current_stock,
            daily_sales_average=inv.daily_sales_average,
            recent_sales=inv.daily_sales_average,
            store_reliability=store.reliability_score
        )

        candidate_stores.append({
            "store_id": store.id,
            "store_name": store.name,
            "address": store.address,
            "latitude": store.latitude,
            "longitude": store.longitude,
            "distance_km": dist_km,
            "price": inv.price,
            "current_stock": inv.current_stock,
            "availability_confidence": avail_conf,
            "stockout_risk_24h": stockout_risk,
            "last_updated": inv.last_updated,
            "store_reliability": store.reliability_score
        })

    # Step 4: Rank Candidates using deterministic heuristics
    ranked_recs = ranking_engine.rank_stores(
        candidate_stores=candidate_stores,
        max_radius_km=intent.radius_km or 5.0,
        max_budget=intent.max_price,
        freshness_priority=intent.freshness_priority or "medium"
    )

    # Step 5: Generate Summary Explanation
    if ranked_recs:
        top = ranked_recs[0]
        explanation = llm_service.explain_recommendation(
            store_name=top.store_name,
            score=top.recommendation_score,
            evidence=top.evidence
        )
    else:
        explanation = "No nearby stores found matching your search radius and product requirements."

    return SearchResponse(
        query=request.query or intent.product,
        intent=intent,
        matched_product=matched_p_out,
        recommendations=ranked_recs,
        explanation=explanation
    )
