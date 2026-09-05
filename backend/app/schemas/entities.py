from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date, datetime

class IntentParseRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Find me fresh Amul milk under 70 rupees within 3 km"})
    user_latitude: Optional[float] = 28.6139
    user_longitude: Optional[float] = 77.2090

class StructuredIntent(BaseModel):
    product: str
    category: Optional[str] = "groceries"
    max_price: Optional[float] = None
    radius_km: Optional[float] = 5.0
    freshness_priority: Optional[str] = "medium" # low, medium, high

class IntentParseResponse(BaseModel):
    query: str
    intent: StructuredIntent
    source: str = Field(..., description="'llm' or 'fallback_regex'")
    error: Optional[str] = None

class StoreOut(BaseModel):
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    reliability_score: float

    model_config = ConfigDict(from_attributes=True)

class ProductOut(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    package_size: Optional[str] = None
    price_range: Optional[str] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class StoreRecommendation(BaseModel):
    store_id: int
    store_name: str
    address: str
    latitude: float
    longitude: float
    distance_km: float
    price: float
    current_stock: int
    availability_confidence: float # e.g. 0.94 -> 94%
    stockout_risk_24h: float        # e.g. 0.08 -> 8%
    last_updated_minutes_ago: float
    store_reliability: float
    recommendation_score: float     # Combined business score 0-100
    is_best_option: bool
    evidence: List[str]
    is_data_stale: bool = False

class SearchRequest(BaseModel):
    query: Optional[str] = None
    product_name: Optional[str] = None
    category: Optional[str] = None
    max_price: Optional[float] = None
    radius_km: Optional[float] = 5.0
    user_latitude: float = 28.6139
    user_longitude: float = 77.2090
    freshness_priority: Optional[str] = "medium"

class SearchResponse(BaseModel):
    query: str
    intent: StructuredIntent
    matched_product: Optional[ProductOut] = None
    recommendations: List[StoreRecommendation]
    demo_scenario: Optional[str] = None
    explanation: str

class FreshnessCalculateRequest(BaseModel):
    manufacturing_date: Optional[str] = None # YYYY-MM-DD
    expiry_date: Optional[str] = None       # YYYY-MM-DD
    scanned_date: Optional[str] = None      # default today

class FreshnessCalculateResponse(BaseModel):
    manufacturing_date: Optional[str] = None
    expiry_date: Optional[str] = None
    total_shelf_life_days: Optional[int] = None
    remaining_shelf_life_days: Optional[int] = None
    freshness_percentage: float
    status: str # FRESH, GOOD, USE_SOON, NEAR_EXPIRY, EXPIRED, INVALID_DATES, MISSING_EXPIRY
    evidence: List[str]

class ProductScanRequest(BaseModel):
    image_base64: Optional[str] = None
    sample_filename: Optional[str] = None # For demo presets
    target_product_name: Optional[str] = None

class ProductScanResponse(BaseModel):
    ocr_text: str
    detected_brand: Optional[str] = None
    detected_product_name: Optional[str] = None
    detected_mfd: Optional[str] = None
    detected_exp: Optional[str] = None
    detected_batch: Optional[str] = None
    ocr_confidence: float
    cv_match_status: str # Likely Match, Uncertain, Mismatch
    cv_confidence: float
    freshness: FreshnessCalculateResponse
    evidence: List[str]
    error: Optional[str] = None
