import pytest
import io
from app.database import SessionLocal
from app.models import Inventory, Transaction, AuditEvent, CommerceEvent
from app.services.ingestion import ingestion_service
from app.routers.events import upload_csv_events

def test_sale_event_ingestion_mutates_inventory_and_revenue():
    db = SessionLocal()
    try:
        inv_before = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == 1).first()
        initial_stock = inv_before.current_stock

        # Ingest SALE event
        ce = ingestion_service.ingest_event(db, {
            "event_type": "SALE",
            "source": "POS_API",
            "store_id": 1,
            "product_id": 1,
            "quantity": 2,
            "unit_price": 65.0,
            "payment_status": "COMPLETED"
        })

        assert ce.event_type == "SALE"
        assert ce.total_amount == 130.0

        # Verify inventory stock was decremented by 2
        db.expire_all()
        inv_after = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == 1).first()
        assert inv_after.current_stock == max(0, initial_stock - 2)

    finally:
        db.close()

def test_payment_failure_event_creates_audit_record():
    db = SessionLocal()
    try:
        audit_count_before = db.query(AuditEvent).count()

        ce = ingestion_service.ingest_event(db, {
            "event_type": "PAYMENT_FAILURE",
            "source": "RAZORPAY",
            "store_id": 1,
            "product_id": 1,
            "quantity": 1,
            "unit_price": 65.0,
            "payment_status": "FAILED",
            "failure_reason": "BANK_TIMEOUT"
        })

        assert ce.event_type == "PAYMENT_FAILURE"
        assert ce.payment_status == "FAILED"

        audit_count_after = db.query(AuditEvent).count()
        assert audit_count_after > audit_count_before

    finally:
        db.close()

def test_stock_replenishment_increases_inventory():
    db = SessionLocal()
    try:
        inv_before = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == 1).first()
        initial_stock = inv_before.current_stock

        ce = ingestion_service.ingest_event(db, {
            "event_type": "STOCK_REPLENISHMENT",
            "source": "INVENTORY_API",
            "store_id": 1,
            "product_id": 1,
            "quantity": 50
        })

        db.expire_all()
        inv_after = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == 1).first()
        assert inv_after.current_stock == initial_stock + 50

    finally:
        db.close()

def test_return_event_restores_stock():
    db = SessionLocal()
    try:
        inv_before = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == 2).first()
        initial_stock = inv_before.current_stock

        ce = ingestion_service.ingest_event(db, {
            "event_type": "RETURN",
            "source": "POS_API",
            "store_id": 1,
            "product_id": 2,
            "quantity": 3
        })

        db.expire_all()
        inv_after = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == 2).first()
        assert inv_after.current_stock == initial_stock + 3

    finally:
        db.close()
