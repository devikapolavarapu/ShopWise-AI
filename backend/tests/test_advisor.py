import pytest
from app.database import SessionLocal
from app.services.advisor import merchant_advisor

def test_what_should_i_do_today_engine():
    db = SessionLocal()
    try:
        actions = merchant_advisor.get_what_to_do_today(db)
        assert len(actions) >= 3, "Hero advisor engine should return top actions"

        # Check action types present in platform decision suite
        action_types = [a["action_type"] for a in actions]
        assert any(t in ["RESTOCK", "PAYMENT_RECOVERY", "WATCH", "PROMOTE"] for t in action_types)

        # Check evidence present
        for act in actions:
            assert "headline" in act
            assert "estimated_impact" in act
            assert len(act["evidence"]) >= 1
    finally:
        db.close()

def test_ask_merchant_advisor():
    db = SessionLocal()
    try:
        res = merchant_advisor.ask_merchant_advisor(query="What should I restock today?", db=db)
        assert "query" in res
        assert "advice" in res
        assert len(res["advice"]) > 10
    finally:
        db.close()

def test_advisor_product_vs_payment_routing_regression():
    db = SessionLocal()
    try:
        # Product restock query must NOT return Razorpay Checkout Gateway
        res_prod = merchant_advisor.ask_merchant_advisor(query="Why should I restock Amul Milk?", db=db)
        assert "Razorpay" not in res_prod["advice"], "Product restock query must not return Razorpay Gateway"
        assert "Amul Milk" in res_prod["advice"] or "demand" in res_prod["advice"].lower()

        # Payment query must return payment gateway advice
        res_pay = merchant_advisor.ask_merchant_advisor(query="Why are checkouts failing on Razorpay?", db=db)
        assert "Payment" in res_pay["advice"] or "payment" in res_pay["advice"].lower() or "gateway" in res_pay["advice"].lower()
    finally:
        db.close()

