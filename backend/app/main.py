from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, SessionLocal, Base
from app.utils.seed_data import seed_database
from app.services.simulation import simulation_service
from app.routers import health, intent, search, store, product, scan, merchant, advisor, demo, simulation, events

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ShopWise AI - Real-Time Commerce Intelligence & Event Ingestion Platform"
)

# Enable CORS for Frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(health.router)
app.include_router(intent.router)
app.include_router(search.router)
app.include_router(store.router)
app.include_router(product.router)
app.include_router(scan.router)
app.include_router(merchant.router)
app.include_router(advisor.router)
app.include_router(demo.router)
app.include_router(simulation.router)
app.include_router(events.router)

@app.on_event("startup")
def startup_event():
    print("[Startup] Initializing Database & Seed Data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from sqlalchemy import text
        try:
            db.execute(text("ALTER TABLE transactions ADD COLUMN source VARCHAR DEFAULT 'DEMO_SIMULATOR'"))
            db.commit()
        except Exception:
            db.rollback()
        seed_database(db)
    finally:
        db.close()
    
    # Auto-start Live Simulation Service
    simulation_service.start()
    print("[Startup] ShopWise AI Backend Server, Event Ingestion & SSE Stream are Ready!")

@app.on_event("shutdown")
def shutdown_event():
    simulation_service.stop()

@app.get("/")
def root():
    return {
        "message": "Welcome to ShopWise AI - Real-Time Commerce Intelligence Platform",
        "docs": "/docs",
        "health": "/api/health",
        "simulation": "/api/simulation/status",
        "events_stream": "/api/events/stream"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
