from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db

router = APIRouter(prefix="/api", tags=["Demo Scenarios"])

DEMO_SCENARIOS = [
    {
        "id": "rising_demand_stockout",
        "title": "Scenario 1: Rising Demand + Stockout Risk",
        "description": "Amul Milk demand grew +18% while inventory covers <1 day (~₹300 revenue at risk).",
        "target_tab": "merchant",
        "recommended_query": "What should I restock today?"
    },
    {
        "id": "revenue_at_risk",
        "title": "Scenario 2: Revenue at Risk Analysis",
        "description": "Quantifies total potential lost sales across stores with impending stockouts.",
        "target_tab": "merchant",
        "recommended_query": "Where am I at risk of losing revenue?"
    },
    {
        "id": "declining_product",
        "title": "Scenario 3: Declining Demand Alert",
        "description": "Identifies products losing demand (-15% growth) to adjust purchase orders.",
        "target_tab": "merchant",
        "recommended_query": "Which products are losing demand?"
    },
    {
        "id": "high_inventory_low_demand",
        "title": "Scenario 4: High Stock + Low Demand",
        "description": "Aashirvaad Atta is overstocked (85 units) -> Recommend weekend promotional bundle.",
        "target_tab": "merchant",
        "recommended_query": "What should I promote?"
    },
    {
        "id": "expiry_risk",
        "title": "Scenario 5: Expiry & Freshness Risk",
        "description": "Batch BR-2026-B088 has <10% shelf life remaining (1 day left) -> Flagged for clearance.",
        "target_tab": "merchant",
        "recommended_query": "Which products are approaching expiry?"
    },
    {
        "id": "geographical_demand",
        "title": "Scenario 6: Spatial Demand Opportunity",
        "description": "High spatial demand cluster in Khan Market with low store availability.",
        "target_tab": "merchant",
        "recommended_query": "Where is demand coming from?"
    },
    {
        "id": "consumer_discovery",
        "title": "Scenario 7: Consumer Product Discovery",
        "description": "Consumer searches for fresh Amul milk under ₹70 within 3 km -> Store A recommended.",
        "target_tab": "discovery",
        "recommended_query": "Find fresh Amul milk under 70 rupees within 3 km"
    },
    {
        "id": "ocr_failure",
        "title": "Scenario 8: OCR Label Failure & Retake",
        "description": "Label text blurry -> Prompts user to retake product image gracefully.",
        "target_tab": "scan",
        "sample_preset": "ocr_failed"
    },
    {
        "id": "stale_inventory",
        "title": "Scenario 9: Stale Inventory Penalty",
        "description": "Store inventory updated 9.5h ago -> Availability confidence penalized by 30%.",
        "target_tab": "discovery",
        "recommended_query": "Check Amul milk stock at Modern Bazaar"
    },
    {
        "id": "llm_fallback",
        "title": "Scenario 10: Groq LLM Fallback Engine",
        "description": "API Key absent/offline -> Deterministic regex parser extracts intent & metrics cleanly.",
        "target_tab": "merchant",
        "recommended_query": "Where am I losing money?"
    }
]

@router.get("/demo/scenarios")
def get_demo_scenarios():
    return {
        "scenarios_count": len(DEMO_SCENARIOS),
        "scenarios": DEMO_SCENARIOS
    }
