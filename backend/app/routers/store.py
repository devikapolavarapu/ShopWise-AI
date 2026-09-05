from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Store
from app.schemas.entities import StoreOut
from app.services.geo import haversine_distance, get_osrm_route

router = APIRouter(prefix="/api", tags=["Stores"])

@router.get("/stores/nearby", response_model=List[StoreOut])
def get_nearby_stores(user_lat: float = 28.6139, user_lon: float = 77.2090, db: Session = Depends(get_db)):
    stores = db.query(Store).all()
    # Sort stores by distance
    stores.sort(key=lambda s: haversine_distance(user_lat, user_lon, s.latitude, s.longitude))
    return stores

@router.get("/stores/{store_id}", response_model=StoreOut)
def get_store_by_id(store_id: int, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store

@router.get("/stores/{store_id}/route")
def get_route_to_store(store_id: int, user_lat: float = 28.6139, user_lon: float = 77.2090, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    route_info = get_osrm_route(user_lat, user_lon, store.latitude, store.longitude)
    return {
        "store_id": store.id,
        "store_name": store.name,
        "destination": {"latitude": store.latitude, "longitude": store.longitude},
        "origin": {"latitude": user_lat, "longitude": user_lon},
        "route": route_info
    }
