from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import AuditEvent
from app.services.simulation import simulation_service

router = APIRouter(prefix="/api/simulation", tags=["Live Simulation Engine"])

class TriggerEventRequest(BaseModel):
    event_type: str = Field(..., json_schema_extra={"example": "demand_spike"}) # demand_spike, 10_purchases, stock_replenished, payment_failure_spike, product_returns, clear_expiry_risk

@router.post("/start")
def start_simulation():
    simulation_service.start()
    return simulation_service.get_status()

@router.post("/stop")
def stop_simulation():
    simulation_service.stop()
    return simulation_service.get_status()

@router.get("/status")
def get_simulation_status():
    return simulation_service.get_status()

@router.post("/trigger-event")
def trigger_simulation_event(request: TriggerEventRequest):
    return simulation_service.trigger_event(request.event_type)

@router.post("/trigger/{event_type}")
def trigger_simulation_event_path(event_type: str):
    return simulation_service.trigger_event(event_type)

@router.get("/audit-trail")
def get_audit_trail(limit: int = Query(15, ge=1, le=100), db: Session = Depends(get_db)):
    audits = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
    results = []
    for a in audits:
        results.append({
            "id": a.id,
            "timestamp": a.timestamp.strftime("%H:%M:%S"),
            "event_type": a.event_type,
            "description": a.description,
            "financial_impact": a.financial_impact,
            "recommendation": a.recommendation
        })
    return {
        "count": len(results),
        "audits": results
    }
