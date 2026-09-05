import os
import random
from datetime import datetime, timezone, timedelta, date
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models import User, Product, Store, Inventory, InventoryHistory, ProductBatch, Transaction

def seed_database(db: Session, force: bool = False):
    if force:
        Base.metadata.drop_all(bind=engine)
    # Reset existing tables
    Base.metadata.create_all(bind=engine)
    
    # Force re-seeding if requested
    if not force and db.query(Transaction).count() > 0:
        print("[DB] Database already seeded with transactions.")
        return

    print("[DB] Clearing and re-seeding database with 850+ realistic merchant transactions...")
    db.query(Transaction).delete()
    db.query(ProductBatch).delete()
    db.query(InventoryHistory).delete()
    db.query(Inventory).delete()
    db.query(Store).delete()
    db.query(Product).delete()
    db.query(User).delete()
    db.commit()

    # 1. Users
    user = User(
        name="Rahul Sharma",
        latitude=28.6139,
        longitude=77.2090  # Connaught Place, New Delhi
    )
    db.add(user)

    # 2. Indian Retail Products
    products_data = [
        {"name": "Amul Taaza Toned Fresh Milk 1L", "brand": "Amul", "category": "Dairy", "package_size": "1L", "price_range": "₹60 - ₹70"},
        {"name": "Britannia 100% Whole Wheat Bread 400g", "brand": "Britannia", "category": "Bakery", "package_size": "400g", "price_range": "₹40 - ₹50"},
        {"name": "Aashirvaad Shudh Chakki Atta 5kg", "brand": "Aashirvaad", "category": "Staples", "package_size": "5kg", "price_range": "₹250 - ₹280"},
        {"name": "Mother Dairy Fresh Paneer 200g", "brand": "Mother Dairy", "category": "Dairy", "package_size": "200g", "price_range": "₹90 - ₹100"},
        {"name": "Tata Salt Vacuum Evaporated Salt 1kg", "brand": "Tata", "category": "Staples", "package_size": "1kg", "price_range": "₹25 - ₹30"},
        {"name": "Surf Excel Easy Wash Detergent Powder 1kg", "brand": "Surf Excel", "category": "Household", "package_size": "1kg", "price_range": "₹130 - ₹150"},
        {"name": "Parle-G Glucose Biscuits 250g", "brand": "Parle", "category": "Snacks", "package_size": "250g", "price_range": "₹25 - ₹35"},
    ]

    products = []
    for p in products_data:
        prod = Product(**p)
        db.add(prod)
        products.append(prod)

    db.flush()

    # 3. Stores around CP, New Delhi
    stores_data = [
        {"name": "FreshMart Supermarket", "address": "Connaught Place Outer Circle, New Delhi", "latitude": 28.6328, "longitude": 77.2197, "reliability_score": 0.98},
        {"name": "DailyNeeds Express", "address": "Janpath Road, New Delhi", "latitude": 28.6250, "longitude": 77.2180, "reliability_score": 0.85},
        {"name": "Modern Bazaar", "address": "Khan Market, New Delhi", "latitude": 28.6000, "longitude": 77.2270, "reliability_score": 0.95},
        {"name": "Reliance Smart Point", "address": "Paharganj, New Delhi", "latitude": 28.6410, "longitude": 77.2120, "reliability_score": 0.88},
        {"name": "Organic Pantry", "address": "Barakhamba Road, New Delhi", "latitude": 28.6290, "longitude": 77.2250, "reliability_score": 0.94},
    ]

    stores = []
    for s in stores_data:
        st = Store(**s)
        db.add(st)
        stores.append(st)

    db.flush()

    # Base price map per product
    prices = {
        1: 65.0,  # Amul Milk
        2: 45.0,  # Britannia Bread
        3: 260.0, # Aashirvaad Atta
        4: 95.0,  # Mother Dairy Paneer
        5: 28.0,  # Tata Salt
        6: 140.0, # Surf Excel
        7: 30.0,  # Parle-G
    }

    now = datetime.now(timezone.utc)

    # 4. Inventories
    for store in stores:
        for product in products:
            p_id = product.id
            s_id = store.id
            base_price = prices.get(p_id, 50.0)

            if p_id == 1 and s_id == 1:
                # FreshMart - Amul Milk (High Stock 32, demand 52/day)
                stock = 32
                daily_sales = 52.0
                last_upd = now - timedelta(minutes=18)
            elif p_id == 1 and s_id == 2:
                # DailyNeeds - Amul Milk (Low Stock 3, High Stockout Risk)
                stock = 3
                daily_sales = 45.0
                last_upd = now - timedelta(minutes=45)
            elif p_id == 1 and s_id == 3:
                # Modern Bazaar - Amul Milk (Stale inventory)
                stock = 15
                daily_sales = 30.0
                last_upd = now - timedelta(hours=9.5)
            elif p_id == 3 and s_id == 1:
                # FreshMart - Aashirvaad Atta (Overstocked 85 units, low demand 12/day)
                stock = 85
                daily_sales = 12.0
                last_upd = now - timedelta(minutes=30)
            else:
                stock = random.randint(10, 60)
                daily_sales = float(random.randint(8, 25))
                last_upd = now - timedelta(minutes=random.randint(15, 300))

            inv = Inventory(
                store_id=s_id,
                product_id=p_id,
                current_stock=stock,
                daily_sales_average=daily_sales,
                last_updated=last_upd,
                price=base_price
            )
            db.add(inv)

    # 5. Generate 850+ Synthetic Transactions over last 30 days
    customers = [f"CUST-{1000 + i}" for i in range(1, 61)] # 60 distinct customer IDs
    txn_count = 0
    start_time = now - timedelta(days=30)

    # Pre-defined customer purchase frequency cohorts (e.g. CUST-1001 to 1015 buy milk every ~5.8 days)
    for day_offset in range(31):
        current_day_dt = start_time + timedelta(days=day_offset)
        is_today = (day_offset == 30)
        
        # Day of week demand factor (weekends higher demand)
        day_factor = 1.3 if current_day_dt.weekday() >= 5 else 1.0
        
        # Growth trend factor (recent 7 days have +18% demand growth for Amul Milk)
        growth_factor = 1.25 if day_offset >= 23 else 1.0

        for store in stores:
            for product in products:
                # Number of transactions for this product at this store today
                if product.id == 1: # Amul Milk (High Volume)
                    num_txns = int(random.randint(3, 8) * day_factor * growth_factor)
                elif product.id == 2: # Bread
                    num_txns = int(random.randint(2, 6) * day_factor)
                elif product.id == 3: # Atta (Lower frequency, larger amount)
                    num_txns = random.randint(1, 3)
                else:
                    num_txns = random.randint(1, 4)

                if is_today:
                    num_txns = max(1, num_txns // 2) # Partial day count for today

                for _ in range(num_txns):
                    txn_count += 1
                    txn_id = f"TXN-{current_day_dt.strftime('%Y%m%d')}-{txn_count:04d}"
                    
                    # Random time during business hours (8 AM to current hour if today, else 9 PM)
                    max_h = min(20, max(8, now.hour)) if is_today else 20
                    min_h = 8 if max_h >= 8 else 0
                    hour = random.randint(min_h, max_h) if max_h >= min_h else 8
                    minute = random.randint(0, 59)
                    txn_timestamp = current_day_dt.replace(hour=hour, minute=minute, second=random.randint(0, 59))

                    # Assign customer (cohort binding for realistic repurchase frequency)
                    cust_idx = (product.id * 7 + txn_count) % len(customers)
                    cust_id = customers[cust_idx]

                    # Quantity & Price
                    qty = random.choices([1, 2, 3], weights=[0.65, 0.25, 0.10])[0]
                    u_price = prices[product.id]
                    tot_amount = round(qty * u_price, 2)

                    txn = Transaction(
                        transaction_id=txn_id,
                        timestamp=txn_timestamp,
                        store_id=store.id,
                        product_id=product.id,
                        quantity=qty,
                        unit_price=u_price,
                        total_amount=tot_amount,
                        customer_id=cust_id,
                        payment_status="COMPLETED"
                    )
                    db.add(txn)

    # 6. Inventory History (30 Days)
    start_date = date.today() - timedelta(days=30)
    for store in stores:
        for product in products:
            opening = random.randint(30, 70)
            for day_offset in range(30):
                d = start_date + timedelta(days=day_offset)
                sold = min(opening, random.randint(8, 25))
                closing = opening - sold
                
                history = InventoryHistory(
                    store_id=store.id,
                    product_id=product.id,
                    date=d,
                    opening_stock=opening,
                    units_sold=sold,
                    closing_stock=closing
                )
                db.add(history)
                opening = closing + random.randint(10, 30)

    # 7. Product Batches for Freshness & Expiry Risk Analysis
    today_date = date.today()
    batches_data = [
        # Store 1 - Amul Milk - FRESH (MFD: 2 days ago, EXP: 12 days in future)
        {"store_id": 1, "product_id": 1, "batch_number": "AM-2026-B101", "mfd": today_date - timedelta(days=2), "exp": today_date + timedelta(days=12)},
        # Store 1 - Britannia Bread - NEAR EXPIRY (<10% shelf life, 1 day left) -> Expiry Risk
        {"store_id": 1, "product_id": 2, "batch_number": "BR-2026-B088", "mfd": today_date - timedelta(days=6), "exp": today_date + timedelta(days=1)},
        # Store 2 - Amul Milk - NEAR EXPIRY (MFD: 10 days ago, EXP: today + 1 day)
        {"store_id": 2, "product_id": 1, "batch_number": "AM-2026-B099", "mfd": today_date - timedelta(days=10), "exp": today_date + timedelta(days=1)},
        # Store 3 - Amul Milk - EXPIRED (MFD: 20 days ago, EXP: 2 days ago)
        {"store_id": 3, "product_id": 1, "batch_number": "AM-2026-B080", "mfd": today_date - timedelta(days=20), "exp": today_date - timedelta(days=2)},
    ]

    for b in batches_data:
        pb = ProductBatch(
            store_id=b["store_id"],
            product_id=b["product_id"],
            batch_number=b["batch_number"],
            manufacturing_date=b["mfd"],
            expiry_date=b["exp"]
        )
        db.add(pb)

    db.commit()
    print(f"[DB] Database seeding completed successfully. Created {txn_count} synthetic transactions.")

if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db, force=True)
    db.close()
