import json
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
from sqlalchemy.orm import Session
from app.models import CommerceEvent, Transaction, Inventory, Product, Store, AuditEvent

class EventIngestionService:
    def __init__(self):
        self._subscribers: List[asyncio.Queue] = []

    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subscribers.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self._subscribers:
            self._subscribers.remove(q)

    async def broadcast_event(self, event_data: Dict[str, Any]):
        for q in list(self._subscribers):
            try:
                await q.put(event_data)
            except Exception:
                pass

    def ingest_event(self, db: Session, event_data: Dict[str, Any]) -> CommerceEvent:
        """
        Validates, persists, mutates state, logs audit entry, and broadcasts a CommerceEvent.
        """
        event_type = event_data.get("event_type", "SALE")
        source = event_data.get("source", "DEMO_SIMULATOR")
        store_id = event_data.get("store_id", 1)
        product_id = event_data.get("product_id", 1)
        qty = int(event_data.get("quantity", 1))
        unit_price = float(event_data.get("unit_price", 0.0))
        
        # Calculate total_amount = qty * unit_price
        if unit_price <= 0 and product_id:
            prod = db.query(Product).filter(Product.id == product_id).first()
            inv = db.query(Inventory).filter(Inventory.store_id == store_id, Inventory.product_id == product_id).first()
            unit_price = inv.price if inv else (65.0 if prod and "Milk" in prod.name else 50.0)

        total_amount = round(qty * unit_price, 2)
        ts_raw = event_data.get("timestamp")
        if isinstance(ts_raw, str):
            try:
                now = datetime.fromisoformat(ts_raw)
            except Exception:
                now = datetime.utcnow()
        elif isinstance(ts_raw, datetime):
            now = ts_raw
        else:
            now = datetime.utcnow()

        event_id = event_data.get("event_id") or f"CE-{now.strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        cust_id = event_data.get("customer_id") or f"CUST-{random.randint(1001, 1060)}"

        # 1. Create & Persist CommerceEvent
        ce = CommerceEvent(
            event_id=event_id,
            event_type=event_type,
            source=source,
            timestamp=now,
            store_id=store_id,
            product_id=product_id,
            quantity=qty,
            unit_price=unit_price,
            total_amount=total_amount,
            customer_id=cust_id,
            payment_status=event_data.get("payment_status", "COMPLETED"),
            metadata_json=json.dumps(event_data.get("metadata", {}))
        )
        db.add(ce)

        # 2. Mutate Inventory & Transactions based on Event Type
        inv = db.query(Inventory).filter(Inventory.store_id == store_id, Inventory.product_id == product_id).first()
        prod = db.query(Product).filter(Product.id == product_id).first()
        prod_name = prod.name if prod else "Item"

        if event_type in ["SALE", "PAYMENT_SUCCESS"]:
            # Persist Transaction
            txn = Transaction(
                transaction_id=f"TXN-{event_id}",
                timestamp=now,
                store_id=store_id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                total_amount=total_amount,
                customer_id=cust_id,
                payment_status="COMPLETED",
                payment_method=event_data.get("payment_method", "UPI"),
                gateway_status="SUCCESS",
                source=source
            )
            db.add(txn)

            # Mutate stock
            if inv:
                old_stock = inv.current_stock
                inv.current_stock = max(0, inv.current_stock - qty)
                inv.last_updated = now

                # Audit threshold check
                if inv.current_stock < 10 and old_stock >= 10:
                    audit = AuditEvent(
                        timestamp=now,
                        event_type="DEMAND_SPIKE",
                        store_id=store_id,
                        product_id=product_id,
                        description=f"Critical Threshold: {prod_name} inventory dropped to {inv.current_stock} units.",
                        metric_changes=json.dumps({"old_stock": old_stock, "new_stock": inv.current_stock}),
                        recommendation=f"RESTOCK {prod_name} immediately",
                        financial_impact=f"₹{int(qty * unit_price * 7)} 7-day stockout risk"
                    )
                    db.add(audit)

        elif event_type == "PAYMENT_FAILURE":
            txn = Transaction(
                transaction_id=f"TXN-{event_id}",
                timestamp=now,
                store_id=store_id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                total_amount=total_amount,
                customer_id=cust_id,
                payment_status="FAILED",
                payment_method=event_data.get("payment_method", "RAZORPAY_CARD"),
                gateway_status="FAILED",
                failure_reason=event_data.get("failure_reason", "BANK_TIMEOUT")
            )
            db.add(txn)

            audit = AuditEvent(
                timestamp=now,
                event_type="PAYMENT_FAILURE",
                store_id=store_id,
                product_id=product_id,
                description=f"Razorpay Payment Failure: Checkout failed for {prod_name} (₹{total_amount}).",
                metric_changes=json.dumps({"lost_amount": total_amount}),
                recommendation="RECOVER — Activate automated payment retry link",
                financial_impact=f"₹{total_amount} checkout value at risk"
            )
            db.add(audit)

        elif event_type == "RETURN":
            if inv:
                inv.current_stock += qty
                inv.last_updated = now

            txn = Transaction(
                transaction_id=f"TXN-{event_id}",
                timestamp=now,
                store_id=store_id,
                product_id=product_id,
                quantity=qty,
                unit_price=unit_price,
                total_amount=-total_amount,
                customer_id=cust_id,
                payment_status="REFUNDED"
            )
            db.add(txn)

            audit = AuditEvent(
                timestamp=now,
                event_type="RETURN",
                store_id=store_id,
                product_id=product_id,
                description=f"Product Return Processed: {qty} units of {prod_name} restored to stock.",
                metric_changes=json.dumps({"returned_qty": qty}),
                recommendation="Inspect product batch quality",
                financial_impact=f"Restored ₹{total_amount} inventory value"
            )
            db.add(audit)

        elif event_type in ["STOCK_REPLENISHMENT", "INVENTORY_UPDATE"]:
            if inv:
                inv.current_stock += qty
                inv.last_updated = now

            audit = AuditEvent(
                timestamp=now,
                event_type="REPLENISHMENT",
                store_id=store_id,
                product_id=product_id,
                description=f"Stock Replenished: +{qty} units added for {prod_name}.",
                metric_changes=json.dumps({"added_qty": qty}),
                recommendation="PROTECT REVENUE — Stock coverage restored",
                financial_impact=f"Protected ₹{int(qty * unit_price)} inventory value"
            )
            db.add(audit)

        db.commit()
        db.refresh(ce)

        # 3. Synchronous / Asynchronous Broadcast to SSE Clients
        event_payload = {
            "id": ce.id,
            "event_id": ce.event_id,
            "event_type": ce.event_type,
            "source": ce.source,
            "timestamp": ce.timestamp.strftime("%H:%M:%S"),
            "product_name": prod_name,
            "quantity": qty,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "payment_status": ce.payment_status,
            "summary": f"{prod_name} × {qty} — ₹{total_amount:.0f} — {ce.event_type}"
        }

        # Broadcast event to active SSE queues
        for q in list(self._subscribers):
            try:
                q.put_nowait(event_payload)
            except Exception:
                pass

        return ce

ingestion_service = EventIngestionService()
