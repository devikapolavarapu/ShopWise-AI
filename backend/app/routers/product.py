from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Product
from app.schemas.entities import ProductOut

router = APIRouter(prefix="/api", tags=["Products"])

@router.get("/products", response_model=List[ProductOut])
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()
