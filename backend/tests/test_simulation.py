import pytest
from app.database import SessionLocal
from app.models import Inventory, Transaction, AuditEvent
from app.services.simulation import simulation_service

def test_simulation_status_and_control():
    status = simulation_service.get_status()
    assert "is_running" in status
    assert "events_processed" in status
    assert "payment_success_rate_pct" in status

def test_process_single_transaction_inventory_mutation():
    db = SessionLocal()
    try:
        inv_before = db.query(Inventory).first()
        initial_stock = inv_before.current_stock
        
        # Process a single live simulated transaction
        event = simulation_service.process_single_transaction()
        assert event is not None
        assert "transaction_id" in event
        assert "status" in event

        # Verify inventory stock was decremented if payment succeeded
        db.expire_all()
        inv_after = db.query(Inventory).filter(Inventory.id == inv_before.id).first()
        if event["status"] == "COMPLETED":
            assert inv_after.current_stock <= initial_stock
    finally:
        db.close()

def test_demand_spike_trigger():
    res = simulation_service.trigger_event("demand_spike")
    assert "Demand Spike triggered" in res["message"]
    assert simulation_service.demand_multiplier == 2.5

def test_payment_failure_spike_trigger():
    res = simulation_service.trigger_event("payment_failure_spike")
    assert "Payment Failure Spike triggered" in res["message"]
    assert simulation_service.payment_failure_rate == 0.25

def test_stock_replenishment_trigger():
    res = simulation_service.trigger_event("stock_replenished")
    assert "Stock replenished" in res["message"]

def test_audit_trail_logging():
    db = SessionLocal()
    try:
        audits = db.query(AuditEvent).all()
        assert isinstance(audits, list)
    finally:
        db.close()
