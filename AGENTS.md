# ShopWise AI - Agent & Modular Design Principles

## Core Agent Principles

1. **Separation of Determinism and Stochastics**:
   - LLMs are **only** used for intent interpretation, query understanding, and plain-English recommendation summaries.
   - LLMs are **never** used for date arithmetic, distance calculation, price filtering, inventory probability, or score ranking.

2. **Evidence-Based Outputs**:
   - All recommendation scores and availability predictions must return clear evidence trails (e.g. stock update timestamp, distance in meters, brand match confidence).

3. **Graceful Fallbacks**:
   - When external services (Groq LLM, external routing APIs, or OCR engines) fail, fallback services immediately engage to ensure continuous core functionality.

4. **Synthetic Data Transparency**:
   - Synthetic inventory data is explicitly marked as "Demo / Simulated Inventory Data".
