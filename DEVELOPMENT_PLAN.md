# ShopWise AI - Development Plan

## Phase Breakdown

- [x] **Phase 1: Project Setup & Architecture Setup**
  - Create directory structure, `ARCHITECTURE.md`, `DEVELOPMENT_PLAN.md`, `AGENTS.md`, `.env.example`.
- [ ] **Phase 2: Backend Core & Database**
  - FastAPI application structure, SQLite database, SQLAlchemy models (`User`, `Product`, `Store`, `Inventory`, `InventoryHistory`, `ProductBatch`).
  - Synthetic data seeder for realistic Indian products and stores.
- [ ] **Phase 3: Geospatial Search & Distance Engine**
  - Haversine distance calculations, OSRM routing interface, Nominatim geocoding fallback.
- [ ] **Phase 4: Inventory Availability Prediction ML**
  - Synthetic history generator, `RandomForestClassifier` training script (`train.py`), model evaluation script (`evaluate.py`), saved artifact.
- [ ] **Phase 5: LLM Intent Parsing Service**
  - `LLMService` wrapper around Groq API, Pydantic strict schemas, graceful regex fallback.
- [ ] **Phase 6: OCR Engine & Deterministic Freshness Engine**
  - Regex & OCR date extractor for MFD/EXP formats, deterministic freshness calculator (shelf life percentage & status).
- [ ] **Phase 7: CV Product Identification & Verification**
  - Product brand/text matcher with confidence scoring and evidence output.
- [ ] **Phase 8: Multi-Criteria Recommendation Engine**
  - Configurable weighted ranking algorithm combining distance, availability, price, reliability, and freshness preference.
- [ ] **Phase 9: API Endpoints & Verification Suite**
  - `/api/intent/parse`, `/api/search`, `/api/stores/nearby`, `/api/inventory/predict`, `/api/product/scan`, `/api/freshness/calculate`, `/api/recommend`, `/api/health`.
  - Automated test suite (`pytest`).
- [ ] **Phase 10: Polished Frontend Application**
  - React + Vite + TypeScript + Tailwind CSS dashboard with Leaflet map, search, store cards, navigation route, product scan verification UI, and Demo Mode switcher.
- [ ] **Phase 11: Demo Scenarios & Polish**
  - 5 deterministic demo scenarios, fallback verification, README documentation, and Mermaid diagrams.
