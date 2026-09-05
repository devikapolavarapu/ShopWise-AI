# ShopWise AI — 3-Minute Hackathon Demo Script & Walkthrough

> **"Turn commerce events into real-time demand, revenue-risk, and merchant decisions."**

This walkthrough provides the official **3-Minute Demo Script** for evaluating **ShopWise AI** during the **Razorpay AI Builder Internship Buildathon 2026**.

---

## 3-Minute Causal Demo Script

### Step 1: Baseline Dashboard & Data Source Disclosure (0:00 - 0:30)
- **Action**: Open [http://localhost:5173](http://localhost:5173).
- **Script**: *"ShopWise AI is a real-time commerce intelligence platform. Notice at the top right: we explicitly badge `LIVE DEMO STREAM (Synthetic Commerce Events)` so evaluator judges know background events are generated locally for architecture demonstration. Here is our baseline: Revenue, Payment Success Rate, and our top Hero Card: What Needs Attention Now?"*
- **Click**: Click **`[ ⏸ Pause Stream ]`** to freeze background events for clean demonstration.

### Step 2: Ingest 10 Purchases (0:30 - 0:50)
- **Action**: Click **`[ 🛍️ 10 Purchases ]`**.
- **Script**: *"I will now trigger 10 purchases. Watch what happens instantly without refreshing the page: 10 SALE events route through our single-path ingestion engine and push over Server-Sent Events (SSE)."*

### Step 3: Observe Causal Changes (0:50 - 1:10)
- **Action**: Point out Orders, Revenue, Inventory, and Event Flow pipeline.
- **Script**: *"Observe the causal chain: Orders increased by exactly +10, Revenue increased by ₹1,033, and total working stock decremented by 10 units. The Causal Pipeline bar shows: EVENT RECEIVED → INGESTED → ANALYZED → DECISION UPDATED."*

### Step 4: RESTOCK Decision (1:10 - 1:30)
- **Action**: Highlight Hero Card #1.
- **Script**: *"Because stock levels dropped, our Financial Decision Engine automatically ranks `#1 RESTOCK` as top priority, calculating ₹9,490 in 7-day revenue at risk from stockouts."*

### Step 5: Execute Restock Action (1:30 - 1:50)
- **Action**: Click **`[ Execute RESTOCK Workflow ]`** on the Hero Card.
- **Script**: *"The merchant clicks 'Execute RESTOCK Workflow'. Stock instantly replenishes by +50 units, protecting revenue, and the audit log records the replenishment event."*

### Step 6: Payment Failure Spike (1:50 - 2:10)
- **Action**: Click **`[ 💳 Payment Failure Spike ]`**.
- **Script**: *"Now let me simulate a Razorpay gateway success rate drop. Watch the payment metrics."*

### Step 7: PAYMENT_RECOVERY Decision (2:10 - 2:30)
- **Action**: Point out Payment Success Rate and Hero Card #1.
- **Script**: *"Gateway success rate drops to 94.5%, failed checkouts rise by +3, and checkout revenue at risk reaches ₹3,315. The decision engine dynamically shifts Hero Priority #1 to `🔴 RECOVER: Recover Failed Checkout Revenue`."*

### Step 8: Execute Recovery Action (2:30 - 2:45)
- **Action**: Click **`[ Execute PAYMENT_RECOVERY Workflow ]`**.
- **Script**: *"Clicking 'Execute PAYMENT_RECOVERY Workflow' triggers an automated payment retry link action for affected checkouts."*

### Step 9: Source Isolation & Supporting Capabilities (2:45 - 3:00)
- **Action**: Switch Data Source dropdown to `Imported CSV`, then point out navbar tabs `Local Discovery` and `Verify Product`.
- **Script**: *"We also support strict Data Source Isolation — switching to 'Imported CSV' isolates external merchant datasets from synthetic events. Supporting features like Consumer Local Discovery and OCR Freshness Verification feed consumer demand signals directly back into the merchant intelligence engine."*

### Step 10: Closing Value Proposition (3:00)
- **Script**: *"ShopWise AI turns raw commerce transaction signals into real-time demand, revenue-risk, and merchant decisions. Thank you!"*

---

## Verified System Status

- **Backend Pytest Suite**: 26/26 tests passed (100%).
- **Frontend Production Build**: Vite build compiled 1,412 modules with 0 errors.
- **Backend API Docs**: `http://localhost:8000/docs`
- **Frontend App**: `http://localhost:5173/`
