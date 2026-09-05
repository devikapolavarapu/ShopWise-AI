# ShopWise AI: Real-Time Commerce Intelligence

ShopWise AI is a real-time commerce intelligence platform for local and growing merchants.

It converts sales, inventory, and payment events into demand signals, financial-risk insights, and actionable merchant decisions instead of requiring merchants to interpret multiple dashboards manually.

> **Synthetic demo transactions, real decision engine.**
>
> The demonstration dataset is synthetic and modeled on realistic retail transactions. Razorpay events shown in the demo are test events, not live production merchant transactions.

---

## Problem

Merchants often have sales, inventory, and payment information spread across different systems.

Knowing that sales happened is not enough. A merchant also needs to know:

- Which products are gaining demand?
- Which products are approaching a stockout?
- How much revenue is at risk because of payment failures?
- Which customers are likely to repurchase?
- What action should be taken now?

ShopWise AI brings these signals together in an event-driven intelligence layer and converts them into measurable business decisions.

---

## What ShopWise AI Does

### 1. Real-Time Commerce Event Intelligence

ShopWise AI accepts commerce events from multiple sources, including:

- Sales
- Inventory updates
- Payment success/failure events
- CSV imports
- Stock replenishment
- Returns
- Razorpay test webhooks

These events are normalized through a common `CommerceEvent` ingestion layer.

The system validates and persists events, updates relevant business state, records audit information, and broadcasts new events to the dashboard using Server-Sent Events (SSE).

---

### 2. Demand & Inventory Intelligence

The platform calculates signals such as:

- Demand velocity
- Inventory coverage
- Stockout risk
- Product movement
- Customer repurchase intervals
- Revenue impact

Instead of only showing inventory numbers, ShopWise AI uses these signals to identify products that need merchant attention.

---

### 3. Payment Intelligence

Payment events are connected to merchant-level financial insights.

The dashboard can surface:

- Payment success rate
- Failed payment activity
- Revenue at risk
- Payment failure trends
- Payment-related recovery actions

Razorpay integration is demonstrated through test/webhook events rather than live production payment data.

---

### 4. AI Merchant Decision Engine

The central goal is not simply to generate AI text.

ShopWise AI combines deterministic commerce metrics with an AI reasoning layer to produce traceable merchant recommendations.

For example:

```text
Commerce Events
      ↓
Demand / Inventory / Payment Metrics
      ↓
Financial Impact
      ↓
AI Decision
      ↓
Merchant Action

```

### 5. Actionable Merchant Workflows

The dashboard prioritizes what needs attention now and provides actions such as:

Restock inventory
Recover payment-related revenue
Review product risk
Investigate commerce events

Actions are reflected back into the system and recorded through the audit trail.

### 6. Product Freshness Verification

ShopWise AI also provides a product verification workflow using OCR.

A product label can be processed to extract relevant text and date information, which can then be used to determine freshness or expiry status.

The OCR workflow is designed to handle both successful extraction and OCR failure cases.

### 7. Consumer Demand & Local Discovery

The project also includes a local discovery layer that connects consumer-side product demand with nearby merchant availability.

It provides structured product discovery and nearby store information while remaining connected to the broader commerce intelligence workflow.

### System Architecture
 ```
                    COMMERCE SOURCES
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
      Sales            Inventory          Payments
        │                  │                  │
        │                  │           Razorpay Test
        │                  │              Webhooks
        └──────────────────┼──────────────────┘
                           ↓
                 CommerceEvent Ingestion
                           │
                 ┌─────────┼─────────┐
                 │         │         │
              Validate   Persist   Audit
                 │         │         │
                 └─────────┼─────────┘
                           ↓
              Business Intelligence Layer
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
     Demand             Inventory          Payment
    Signals              Risk              Risk
        │                  │                  │
        └──────────────────┼──────────────────┘
                           ↓
                Financial Impact Engine
                           ↓
                 AI Decision / Advisor
                           ↓
                Merchant Dashboard
                           │
                    ┌──────┴──────┐
                    ↓             ↓
                REST APIs        SSE
                    │             │
                    └──────┬──────┘
                           ↓
                    Real-Time UI
```
## Technology Stack

### Frontend

- React
- Vite
- JavaScript
- Server-Sent Events (SSE)
- Responsive merchant dashboard

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- REST APIs
- Server-Sent Events

### AI / ML

- Groq / Llama-based AI reasoning
- Deterministic business metrics for grounded recommendations
- Stockout prediction model
- OCR-based product text extraction

### Integrations

- Razorpay test/webhook events
- CSV commerce data ingestion
- Local discovery / maps workflow

---

## Key API Workflows

### Commerce Events

    POST /api/events/...

Commerce events are validated and passed through the common ingestion service.

### Event Stream

    GET /api/events/stream

The dashboard subscribes to the SSE stream for real-time commerce updates.

### CSV Import

    POST /api/events/upload-csv

Imported events retain their source identity so that CSV data can be analyzed independently from demo streams.

### Razorpay Webhooks

    POST /api/webhooks/razorpay

Razorpay test/webhook events are converted into the common commerce-event model.

### Time-Series Analytics

    GET /api/events/time-series

Provides event-derived time-series data for dashboard analytics.

---

## Demo Flow

The project includes deterministic demo controls so that the core event-driven behaviour can be demonstrated consistently.

### Scenario 1 — 10 Purchases

Triggering the purchase scenario creates exactly 10 sale events.

The dashboard reflects:

- Orders increasing by 10
- Revenue increasing
- Inventory decreasing by 10 units
- Real-time SSE event updates
- A corresponding merchant recommendation

The merchant can then execute the suggested restock workflow.

### Scenario 2 — Payment Failure Spike

A payment-failure scenario demonstrates:

- Increased failed payment activity
- Lower payment success rate
- Increased revenue at risk
- A payment recovery recommendation

### Scenario 3 — Stock Replenishment

A replenishment event increases product inventory and updates the dashboard and audit trail.

---

## Data Transparency

The default demonstration commerce data is **synthetic**, but it is modeled to resemble realistic local retail transactions.

The system does not represent the synthetic transactions as real merchant transactions.

Razorpay functionality is demonstrated through test/webhook events and not through private production payment data.

This allows the complete event → analytics → decision workflow to be demonstrated without exposing real customer or payment information.

---

## Why This Approach

ShopWise AI is designed around a simple principle:

> **Do not just show the merchant what happened. Help them understand what needs attention and why.**

The system therefore combines:

**Events → Signals → Financial Impact → AI Reasoning → Action**

This makes the dashboard a decision-support system rather than only a reporting interface.

---

## Project Structure

    ShopWise-AI/
    ├── backend/
    │   ├── app/
    │   ├── tests/
    │   └── requirements.txt
    │
    ├── frontend/
    │   ├── src/
    │   ├── public/
    │   └── package.json
    │
    ├── README.md
    ├── ARCHITECTURE.md
    └── walkthrough.md

---

## Running Locally

### Backend

    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Backend:

    http://localhost:8000

API documentation:

    http://localhost:8000/docs

### Frontend

    cd frontend
    npm install
    npm run dev

Frontend:

    http://localhost:5173

---

## Validation

The project includes automated backend and end-to-end API checks covering:

- Commerce event ingestion
- SSE event delivery
- Purchase simulation
- Payment failure scenarios
- Inventory replenishment
- CSV source isolation
- Payment and revenue analytics
- Product analytics
- Local discovery
- Product freshness workflow
- Numeric formatting
- AI response formatting

The frontend production build is also validated using:

    npm run build

---

## Project Status

ShopWise AI is a working prototype demonstrating a real-time merchant intelligence workflow using synthetic retail data and Razorpay test events.

The focus of the project is on connecting commerce events to measurable merchant decisions rather than presenting isolated AI features.

---

## Built For

**Razorpay AI Builder Internship 2026**

**Track:** Open Track
