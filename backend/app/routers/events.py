import csv
import io
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, Request, Query, Header
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import CommerceEvent, Product, Store, Transaction, Inventory
from app.services.ingestion import ingestion_service

router = APIRouter(prefix="/api", tags=["Event Ingestion & SSE Stream"])

class IngestEventRequest(BaseModel):
    event_type: str = Field("SALE", json_schema_extra={"example": "SALE"}) # SALE, INVENTORY_UPDATE, PAYMENT_SUCCESS, PAYMENT_FAILURE, RETURN, STOCK_REPLENISHMENT
    source: str = Field("POS_API", json_schema_extra={"example": "POS_API"}) # POS_API, INVENTORY_API, RAZORPAY, CSV_IMPORT, DEMO_SIMULATOR
    store_id: int = 1
    product_id: int = 1
    quantity: int = 1
    unit_price: float = 0.0
    customer_id: Optional[str] = "CUST-1001"
    payment_status: Optional[str] = "COMPLETED"
    payment_method: Optional[str] = "UPI"
    failure_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@router.post("/events/ingest")
def ingest_single_event(req: IngestEventRequest, db: Session = Depends(get_db)):
    ce = ingestion_service.ingest_event(db, req.model_dump())
    return {
        "status": "success",
        "event_id": ce.event_id,
        "event_type": ce.event_type,
        "source": ce.source,
        "total_amount": ce.total_amount
    }

@router.post("/events/sale")
def ingest_sale_event(req: IngestEventRequest, db: Session = Depends(get_db)):
    req.event_type = "SALE"
    return ingest_single_event(req, db)

@router.post("/events/inventory")
def ingest_inventory_event(req: IngestEventRequest, db: Session = Depends(get_db)):
    req.event_type = "INVENTORY_UPDATE"
    return ingest_single_event(req, db)

@router.post("/events/payment")
def ingest_payment_event(req: IngestEventRequest, db: Session = Depends(get_db)):
    req.event_type = "PAYMENT_SUCCESS" if req.payment_status == "COMPLETED" else "PAYMENT_FAILURE"
    return ingest_single_event(req, db)

@router.post("/events/return")
def ingest_return_event(req: IngestEventRequest, db: Session = Depends(get_db)):
    req.event_type = "RETURN"
    return ingest_single_event(req, db)

# Server-Sent Events (SSE) Live Stream Endpoint
@router.get("/events/stream")
async def stream_events(request: Request):
    async def event_generator():
        q = ingestion_service.subscribe()
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event_data = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield f"data: {json.dumps(event_data)}\n\n"
                except asyncio.TimeoutError:
                    # Keep-alive heartbeat comment
                    yield f": heartbeat\n\n"
        finally:
            ingestion_service.unsubscribe(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# CSV Import Pipeline
@router.post("/events/upload-csv")
async def upload_csv_events(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    text = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text))

    count = 0
    now = datetime.utcnow()
    products = db.query(Product).all()
    prod_map = {p.name.lower(): p.id for p in products}

    for row in reader:
        count += 1
        prod_name = row.get("product", "").strip().lower()
        product_id = prod_map.get(prod_name, 1)
        qty = int(row.get("quantity", 1))
        unit_price = float(row.get("unit_price", 50.0))
        status = row.get("payment_status", "COMPLETED").strip().upper()

        event_data = {
            "event_type": "SALE" if status == "COMPLETED" else "PAYMENT_FAILURE",
            "source": "CSV_IMPORT",
            "timestamp": now - timedelta(minutes=count),
            "store_id": 1,
            "product_id": product_id,
            "quantity": qty,
            "unit_price": unit_price,
            "customer_id": row.get("customer_id", f"CUST-CSV-{count:03d}"),
            "payment_status": status
        }
        ingestion_service.ingest_event(db, event_data)

    return {
        "status": "success",
        "imported_count": count,
        "message": f"Imported {count} events successfully via CSV",
        "source": "Imported CSV"
    }

# Razorpay Webhook Ingestion Pipeline
@router.post("/webhooks/razorpay")
async def razorpay_webhook_handler(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    event_name = payload.get("event", "payment.authorized")

    # Map Razorpay webhook event to CommerceEvent
    if event_name in ["payment.authorized", "payment.captured", "order.paid"]:
        event_type = "PAYMENT_SUCCESS"
        status = "COMPLETED"
    else:
        event_type = "PAYMENT_FAILURE"
        status = "FAILED"

    payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
    amount = float(payment_entity.get("amount", 6500)) / 100.0 # Razorpay amounts in paise
    method = payment_entity.get("method", "UPI").upper()
    fail_reason = payment_entity.get("error_description", "BANK_TIMEOUT") if status == "FAILED" else None

    event_data = {
        "event_type": event_type,
        "source": "RAZORPAY",
        "timestamp": datetime.utcnow(),
        "store_id": 1,
        "product_id": 1,
        "quantity": 1,
        "unit_price": amount,
        "customer_id": f"CUST-RZP-{payment_entity.get('id', '101')[-4:]}",
        "payment_status": status,
        "payment_method": method,
        "failure_reason": fail_reason,
        "metadata": {"razorpay_event": event_name, "payment_id": payment_entity.get("id")}
    }

    ce = ingestion_service.ingest_event(db, event_data)
    return {
        "status": "accepted",
        "event_id": ce.event_id,
        "source": "Razorpay Test / Webhook"
    }

# Time-Series Chart Points (Last 30 Minutes)
@router.get("/events/time-series")
def get_time_series_data(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    thirty_mins_ago = now - timedelta(minutes=30)

    # 3-minute buckets for 30 minutes (10 points)
    points = []
    for i in range(10):
        b_start = thirty_mins_ago + timedelta(minutes=i * 3)
        b_end = b_start + timedelta(minutes=3)
        b_label = b_start.strftime("%H:%M")

        txns = db.query(Transaction).filter(Transaction.timestamp >= b_start, Transaction.timestamp < b_end).all()
        rev = sum(t.total_amount for t in txns if t.payment_status == "COMPLETED")
        units = sum(t.quantity for t in txns if t.payment_status == "COMPLETED")
        failed = sum(1 for t in txns if t.payment_status == "FAILED")
        succ = sum(1 for t in txns if t.payment_status == "COMPLETED")
        success_rate = round((succ / max(1, succ + failed)) * 100.0, 1)

        points.append({
            "time": b_label,
            "revenue": round(rev, 2),
            "units": units,
            "payment_success_rate": success_rate
        })

    return {"points": points}
