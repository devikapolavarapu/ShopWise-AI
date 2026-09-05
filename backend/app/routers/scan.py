import base64
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.entities import (
    ProductScanRequest, ProductScanResponse,
    FreshnessCalculateRequest, FreshnessCalculateResponse
)
from app.ocr.engine import ocr_engine
from app.cv.matcher import cv_matcher
from app.services.freshness import calculate_freshness
from app.ml.model import predictor

router = APIRouter(prefix="/api", tags=["Product Scan & Verification"])

# Presets for the 5 Hackathon Demo Scenarios
DEMO_PRESETS = {
    "fresh_milk": {
        "text": "AMUL TAAZA TONED MILK\nMFD: 15/08/2026\nEXP: 28/08/2026\nBATCH: AM-B101\nNET VOL: 1L",
        "target_product": "Amul Milk"
    },
    "near_expiry_milk": {
        "text": "AMUL TAAZA TONED MILK\nMFD: 10/08/2026\nEXP: 26/08/2026\nBATCH: AM-B099\nNET VOL: 1L",
        "target_product": "Amul Milk"
    },
    "expired_product": {
        "text": "BRITANNIA BREAD 100% WHEAT\nMFD: 10/08/2026\nEXP: 22/08/2026\nBATCH: BR-B80\nNET WT: 400g",
        "target_product": "Britannia Bread"
    },
    "ocr_failed": {
        "text": "BLURRY UNREADABLE PACKAGING TEXT ### @@@ ---",
        "target_product": "Amul Milk"
    }
}

@router.post("/freshness/calculate", response_model=FreshnessCalculateResponse)
def calculate_freshness_endpoint(req: FreshnessCalculateRequest):
    return calculate_freshness(
        mfd_str=req.manufacturing_date,
        exp_str=req.expiry_date,
        scanned_date_str=req.scanned_date
    )

@router.post("/product/scan", response_model=ProductScanResponse)
def scan_product_label(req: ProductScanRequest):
    target = req.target_product_name or "Amul Milk"

    # Scenario 1: Preset Sample
    if req.sample_filename and req.sample_filename in DEMO_PRESETS:
        preset = DEMO_PRESETS[req.sample_filename]
        ocr_text = preset["text"]
        target = preset["target_product"]
        ocr_conf = 0.95 if req.sample_filename != "ocr_failed" else 0.25
    elif req.image_base64:
        try:
            image_data = base64.b64decode(req.image_base64.split(",")[-1])
            ocr_text, ocr_conf = ocr_engine.extract_text_from_image(image_data)
        except Exception as e:
            ocr_text = ""
            ocr_conf = 0.0
    else:
        # Default mock fallback scan if no image provided
        preset = DEMO_PRESETS["fresh_milk"]
        ocr_text = preset["text"]
        ocr_conf = 0.92

    # Step 1: Parse OCR Text
    parsed_label = ocr_engine.parse_product_label_text(ocr_text)

    mfd = parsed_label["mfd"]
    exp = parsed_label["exp"]
    batch = parsed_label["batch"]
    brand = parsed_label["brand"]

    # Step 2: CV Matcher
    match_status, cv_conf, cv_evidence = cv_matcher.match_product(
        extracted_text=ocr_text,
        detected_brand=brand,
        target_product_name=target
    )

    # Step 3: Freshness Calculation
    freshness_res = calculate_freshness(mfd_str=mfd, exp_str=exp)

    # Combined Evidence
    combined_evidence = []
    combined_evidence.extend(cv_evidence)
    combined_evidence.extend(freshness_res.evidence)
    if batch:
        combined_evidence.append(f"Batch Number detected: {batch}")

    error_msg = None
    if ocr_conf < 0.30 or freshness_res.status in ["MISSING_EXPIRY", "INVALID_DATES"]:
        error_msg = "Could not reliably read the expiry date. Please retake the image."

    return ProductScanResponse(
        ocr_text=ocr_text,
        detected_brand=brand,
        detected_product_name=target if match_status == "Likely Match" else None,
        detected_mfd=mfd,
        detected_exp=exp,
        detected_batch=batch,
        ocr_confidence=ocr_conf,
        cv_match_status=match_status,
        cv_confidence=cv_conf,
        freshness=freshness_res,
        evidence=combined_evidence,
        error=error_msg
    )

@router.post("/inventory/predict")
def predict_stockout_risk(
    current_stock: int,
    daily_sales_average: float,
    recent_sales: float = None,
    store_reliability: float = 0.95
):
    avail_conf, risk = predictor.predict_availability(
        current_stock=current_stock,
        daily_sales_average=daily_sales_average,
        recent_sales=recent_sales,
        store_reliability=store_reliability
    )
    return {
        "current_stock": current_stock,
        "daily_sales_average": daily_sales_average,
        "availability_confidence": avail_conf,
        "stockout_risk_24h": risk
    }
