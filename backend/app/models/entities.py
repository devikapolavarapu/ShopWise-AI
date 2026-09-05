from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, default="Default User")
    latitude = Column(Float, default=28.6139) # Default New Delhi (Connaught Place)
    longitude = Column(Float, default=77.2090)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    brand = Column(String, index=True)
    category = Column(String, index=True)
    package_size = Column(String)
    price_range = Column(String) # e.g., "₹60 - ₹70"
    image_url = Column(String, nullable=True)

    inventories = relationship("Inventory", back_populates="product")
    history = relationship("InventoryHistory", back_populates="product")
    batches = relationship("ProductBatch", back_populates="product")

class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    reliability_score = Column(Float, default=0.95) # 0.0 to 1.0

    inventories = relationship("Inventory", back_populates="store")
    history = relationship("InventoryHistory", back_populates="store")
    batches = relationship("ProductBatch", back_populates="store")

class Inventory(Base):
    __tablename__ = "inventories"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    current_stock = Column(Integer, default=0)
    daily_sales_average = Column(Float, default=10.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    price = Column(Float, default=50.0)

    store = relationship("Store", back_populates="inventories")
    product = relationship("Product", back_populates="inventories")

class InventoryHistory(Base):
    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    date = Column(Date, index=True)
    opening_stock = Column(Integer)
    units_sold = Column(Integer)
    closing_stock = Column(Integer)

    store = relationship("Store", back_populates="history")
    product = relationship("Product", back_populates="history")

class ProductBatch(Base):
    __tablename__ = "product_batches"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    batch_number = Column(String, index=True)
    manufacturing_date = Column(Date)
    expiry_date = Column(Date)

    store = relationship("Store", back_populates="batches")
    product = relationship("Product", back_populates="batches")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    customer_id = Column(String, index=True)
    payment_status = Column(String, default="COMPLETED") # COMPLETED, FAILED, REFUNDED
    payment_method = Column(String, default="UPI") # UPI, RAZORPAY_CARD, NETBANKING
    gateway_status = Column(String, default="SUCCESS") # SUCCESS, FAILED
    failure_reason = Column(String, nullable=True)
    source = Column(String, default="DEMO_SIMULATOR", index=True)

    store = relationship("Store")
    product = relationship("Product")

class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    event_type = Column(String, index=True) # TRANSACTION, DEMAND_SPIKE, REPLENISHMENT, PAYMENT_FAILURE, EXPIRY_ACTION
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    description = Column(String)
    metric_changes = Column(Text, nullable=True)
    recommendation = Column(String, nullable=True)
    financial_impact = Column(String, nullable=True)

    store = relationship("Store")
    product = relationship("Product")

class CommerceEvent(Base):
    __tablename__ = "commerce_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String, unique=True, index=True)
    event_type = Column(String, index=True) # SALE, INVENTORY_UPDATE, PAYMENT_SUCCESS, PAYMENT_FAILURE, RETURN, STOCK_REPLENISHMENT, DEMAND_SIGNAL
    source = Column(String, index=True, default="DEMO_SIMULATOR") # POS_API, INVENTORY_API, RAZORPAY, CSV_IMPORT, DEMO_SIMULATOR
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    customer_id = Column(String, nullable=True, index=True)
    payment_status = Column(String, default="COMPLETED")
    metadata_json = Column(Text, nullable=True)

    store = relationship("Store")
    product = relationship("Product")
