import time
import random
import threading
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product, Store, Transaction, AuditEvent, Inventory
from app.services.ingestion import ingestion_service

class LiveSimulationEngine:
    def __init__(self):
        self.is_running = False
        self.interval_seconds = 4.0
        self.events_processed = 0
        self.last_event: Optional[Dict[str, Any]] = None
        self.thread: Optional[threading.Thread] = None
        
        # Simulation Parameters
        self.demand_multiplier = 1.0
        self.spike_remaining = 0
        self.payment_failure_rate = 0.018  # 1.8% baseline failure rate
        self.failure_spike_remaining = 0

        # Behavioral Product Selection Weights
        self.product_weights = {
            1: 30, # Amul Milk (High Frequency Repeat)
            2: 20, # Britannia Bread (Frequent)
            3: 10, # Aashirvaad Atta (Lower frequency, higher basket ₹260)
            4: 15, # Mother Dairy Paneer (Moderate/High)
            5: 10, # Tata Salt (Stable)
            6: 5,  # Surf Excel (Periodic)
            7: 10   # Parle-G (Frequent low-value)
        }

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("[Simulation] Event ingestion stream producer started.")

    def stop(self):
        self.is_running = False
        print("[Simulation] Event ingestion stream producer stopped.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "is_running": self.is_running,
            "interval_seconds": self.interval_seconds,
            "events_processed": self.events_processed,
            "last_event": self.last_event,
            "demand_multiplier": round(self.demand_multiplier, 2),
            "payment_failure_rate_pct": round(self.payment_failure_rate * 100.0, 1),
            "payment_success_rate_pct": round((1.0 - self.payment_failure_rate) * 100.0, 1)
        }

    def _run_loop(self):
        while self.is_running:
            try:
                self.process_single_transaction()
            except Exception as e:
                print(f"[Simulation Error] {e}")

            # Check multipliers decay
            if self.spike_remaining > 0:
                self.spike_remaining -= 1
                if self.spike_remaining == 0:
                    self.demand_multiplier = 1.0

            if self.failure_spike_remaining > 0:
                self.failure_spike_remaining -= 1
                if self.failure_spike_remaining == 0:
                    self.payment_failure_rate = 0.018

            time.sleep(self.interval_seconds)

    def process_single_transaction(self) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            # Select Store & Product based on behavioral weights
            stores = db.query(Store).all()
            if not stores:
                return {}
            store = random.choice(stores)

            prod_ids = list(self.product_weights.keys())
            weights = list(self.product_weights.values())
            chosen_pid = random.choices(prod_ids, weights=weights)[0]
            product = db.query(Product).filter(Product.id == chosen_pid).first() or db.query(Product).first()

            qty = random.choices([1, 2, 3], weights=[0.70, 0.20, 0.10])[0]
            if self.demand_multiplier > 1.5:
                qty = random.choices([2, 3, 4], weights=[0.50, 0.35, 0.15])[0]

            is_failed = random.random() < self.payment_failure_rate
            event_type = "PAYMENT_FAILURE" if is_failed else "SALE"
            pm = random.choice(["UPI", "RAZORPAY_CARD", "NETBANKING"])
            fail_reason = random.choice(["BANK_TIMEOUT", "GATEWAY_DEGRADED", "EXPIRED_CARD"]) if is_failed else None

            now = datetime.utcnow()
            event_data = {
                "event_type": event_type,
                "source": "DEMO_SIMULATOR",
                "timestamp": now,
                "store_id": store.id,
                "product_id": product.id,
                "quantity": qty,
                "customer_id": f"CUST-{random.randint(1001, 1060)}",
                "payment_status": "FAILED" if is_failed else "COMPLETED",
                "payment_method": pm,
                "failure_reason": fail_reason
            }

            # Ingest through unified pipeline
            ce = ingestion_service.ingest_event(db, event_data)
            self.events_processed += 1

            self.last_event = {
                "transaction_id": ce.event_id,
                "timestamp": now.strftime("%H:%M:%S"),
                "product_name": product.name,
                "store_name": store.name,
                "quantity": qty,
                "total_amount": ce.total_amount,
                "status": ce.payment_status,
                "event_type": ce.event_type,
                "summary": f"{product.name} × {qty} — ₹{ce.total_amount:.0f} — {ce.event_type}"
            }
            return self.last_event

        finally:
            db.close()

    def trigger_event(self, event_type: str) -> Dict[str, Any]:
        db: Session = SessionLocal()
        now = datetime.utcnow()
        try:
            if event_type == "demand_spike":
                self.demand_multiplier = 2.5
                self.spike_remaining = 15
                for _ in range(3):
                    self.process_single_transaction()
                return {"message": "Demand Spike triggered (+150% demand velocity)", "demand_multiplier": 2.5}

            elif event_type == "10_purchases":
                products = db.query(Product).all()
                if not products:
                    return {"message": "No products available"}
                
                total_added_revenue = 0.0
                created_ids = []

                for i in range(10):
                    prod = products[i % len(products)]
                    inv = db.query(Inventory).filter(Inventory.store_id == 1, Inventory.product_id == prod.id).first()
                    unit_price = inv.price if inv else 65.0
                    qty = 1

                    event_data = {
                        "event_type": "SALE",
                        "source": "DEMO_SIMULATOR",
                        "timestamp": datetime.utcnow(),
                        "store_id": 1,
                        "product_id": prod.id,
                        "quantity": qty,
                        "unit_price": unit_price,
                        "customer_id": f"CUST-{1000 + i}",
                        "payment_status": "COMPLETED",
                        "payment_method": "UPI"
                    }
                    ce = ingestion_service.ingest_event(db, event_data)
                    self.events_processed += 1
                    total_added_revenue += ce.total_amount
                    created_ids.append(ce.event_id)

                self.last_event = {
                    "transaction_id": created_ids[-1],
                    "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
                    "product_name": "10-Purchase Batch",
                    "store_name": "Modern Bazaar",
                    "quantity": 10,
                    "total_amount": total_added_revenue,
                    "status": "COMPLETED",
                    "event_type": "SALE",
                    "summary": f"10-Purchase Batch — ₹{total_added_revenue:.0f} — SALE"
                }

                return {
                    "message": "Successfully ingested 10 SALE events",
                    "events_created_count": 10,
                    "total_revenue_added": total_added_revenue
                }

            elif event_type == "stock_replenished":
                ingestion_service.ingest_event(db, {
                    "event_type": "STOCK_REPLENISHMENT",
                    "source": "INVENTORY_API",
                    "store_id": 1,
                    "product_id": 1,
                    "quantity": 50
                })
                return {"message": "Stock replenished for low-stock products (+50 units)"}

            elif event_type == "payment_failure_spike":
                self.payment_failure_rate = 0.25
                self.failure_spike_remaining = 15
                for i in range(3):
                    ingestion_service.ingest_event(db, {
                        "event_type": "PAYMENT_FAILURE",
                        "source": "RAZORPAY",
                        "store_id": 1,
                        "product_id": (i % 3) + 1,
                        "quantity": 1,
                        "unit_price": 65.0,
                        "customer_id": f"CUST-FAIL-{100 + i}",
                        "payment_status": "FAILED",
                        "payment_method": "RAZORPAY_CARD",
                        "failure_reason": "BANK_TIMEOUT"
                    })
                    self.events_processed += 1
                return {"message": "Payment Failure Spike triggered (3 failed checkouts ingested)"}

            elif event_type == "product_returns":
                ingestion_service.ingest_event(db, {
                    "event_type": "RETURN",
                    "source": "POS_API",
                    "store_id": 1,
                    "product_id": 2,
                    "quantity": 2
                })
                return {"message": "Customer product return processed (+2 units restored)"}

            elif event_type == "clear_expiry_risk":
                ingestion_service.ingest_event(db, {
                    "event_type": "INVENTORY_UPDATE",
                    "source": "POS_API",
                    "store_id": 1,
                    "product_id": 2,
                    "quantity": 0,
                    "metadata": {"action": "CLEARANCE_DISCOUNT_APPLIED"}
                })
                return {"message": "Expiry clearance action logged"}

            return {"message": f"Event {event_type} executed"}

        finally:
            db.close()

simulation_service = LiveSimulationEngine()
