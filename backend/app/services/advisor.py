import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.services.analytics import analytics_service
from app.services.llm import llm_service

class MerchantAdvisorService:
    def get_what_to_do_today(self, db: Session, store_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Returns the top 3 prioritized, evidence-backed merchant actions for today.
        """
        products = analytics_service.get_product_intelligence(db, store_id=store_id)
        expiry_risks = analytics_service.get_expiry_freshness_risks(db, store_id=store_id)

        actions = []
        kpis = analytics_service.get_dashboard_summary(db, store_id=store_id)

        # 0. PAYMENT RECOVERY Action (High Priority if Payment Gateway Failure Spike)
        if kpis.get("failed_orders_24h", 0) > 0 or kpis.get("payment_success_rate", 100.0) < 95.0:
            actions.append({
                "priority": 1,
                "action_type": "PAYMENT_RECOVERY",
                "product_name": "Razorpay Checkout Gateway",
                "headline": "Recover Failed Checkout Revenue",
                "summary": f"Payment success rate dropped to {kpis['payment_success_rate']}% with {kpis['failed_orders_24h']} failed checkouts in 24h.",
                "estimated_impact": f"₹{kpis['payment_failure_revenue_at_risk_24h']:.0f} Revenue at Risk",
                "evidence": [
                    f"Payment gateway success rate: {kpis['payment_success_rate']}% (dropped from 98.2% baseline)",
                    f"{kpis['failed_orders_24h']} failed customer checkout attempts in last 24 hours",
                    f"₹{kpis['payment_failure_revenue_at_risk_24h']:.0f} total lost transaction value",
                    "Recommended Action: Activate Razorpay Automated Payment Retry SMS & UPI Intent Fallback"
                ]
            })

        # 1. RESTOCK / REPLENISH Action (Highest Revenue at Risk or Lowest Stock Coverage)
        restock_candidates = [p for p in products if p["stockout_risk_24h"] >= 0.35 or p["days_stock_remaining"] < 1.5]
        if not restock_candidates:
            restock_candidates = sorted(products, key=lambda x: x["days_stock_remaining"])

        if restock_candidates:
            top_restock = restock_candidates[0]
            repurchase_str = f"Customers typically repurchase every {top_restock['repurchase_interval_days']} days. " if top_restock["repurchase_interval_days"] else ""

            actions.append({
                "priority": len(actions) + 1,
                "action_type": "RESTOCK",
                "product_name": top_restock["product_name"],
                "headline": f"Restock {top_restock['product_name']} Immediately",
                "summary": f"Demand grew {top_restock['demand_growth_pct']:+.1f}% this week while current stock covers only {top_restock['days_stock_remaining']} days of projected demand.",
                "estimated_impact": f"₹{top_restock['revenue_at_risk_7d']:.0f} Revenue at Risk",
                "evidence": [
                    f"{top_restock['units_sold_30d']} units sold across {top_restock['orders_count_30d']} purchase orders in 30 days",
                    f"Demand trend: {top_restock['demand_growth_pct']:+.1f}% growth over previous week",
                    f"Predicted daily demand: {top_restock['avg_daily_demand']} units/day",
                    f"Current stock: {top_restock['current_stock']} units ({top_restock['days_stock_remaining']} days remaining)",
                    f"Predicted 24h Stockout Risk: {int(top_restock['stockout_risk_24h'] * 100)}%",
                    repurchase_str.strip()
                ]
            })

        # 2. WATCH / PROTECT REVENUE Action (Rising Demand Product)
        rising_candidates = [p for p in products if p["demand_trend"] == "RISING" and p["product_name"] != (actions[0]["product_name"] if actions else "")]
        if not rising_candidates:
            rising_candidates = [p for p in products if p["product_name"] != (actions[0]["product_name"] if actions else "")]

        if rising_candidates:
            top_watch = rising_candidates[0]
            actions.append({
                "priority": 2,
                "action_type": "WATCH",
                "product_name": top_watch["product_name"],
                "headline": f"Monitor {top_watch['product_name']} Inventory",
                "summary": f"Steady demand velocity with {top_watch['units_sold_30d']} units sold. Ensure supplier replenishment arrives on schedule.",
                "estimated_impact": f"Protect ₹{top_watch['revenue_30d']:.0f} Monthly Revenue",
                "evidence": [
                    f"{top_watch['units_sold_30d']} total units sold generating ₹{top_watch['revenue_30d']:.0f} in 30d revenue",
                    f"Average daily sales velocity: {top_watch['avg_daily_demand']} units/day",
                    f"Current stock covers approx {top_watch['days_stock_remaining']} days of sales",
                    f"Availability confidence rating: {int(top_watch['availability_confidence'] * 100)}%"
                ]
            })

        # 3. PROMOTE / CLEARANCE Action (Overstocked or Near Expiry)
        if expiry_risks:
            exp_risk = expiry_risks[0]
            actions.append({
                "priority": 3,
                "action_type": "PROMOTE",
                "product_name": exp_risk["product_name"],
                "headline": f"Promote Batch {exp_risk['batch_number']} ({exp_risk['product_name']})",
                "summary": f"{exp_risk['units_at_risk']} units have only {exp_risk['remaining_days']} days ({exp_risk['shelf_life_pct']}% shelf life) remaining before expiry.",
                "estimated_impact": f"Prevent ₹{exp_risk['potential_financial_loss']:.0f} Waste Loss",
                "evidence": [
                    f"Batch {exp_risk['batch_number']} manufacturing date: {exp_risk['manufacturing_date']}, expiry: {exp_risk['expiry_date']}",
                    f"Remaining shelf life: {exp_risk['shelf_life_pct']}% ({exp_risk['remaining_days']} days left)",
                    f"{exp_risk['units_at_risk']} units currently at risk of spoiling",
                    f"Recommended Merchant Action: {exp_risk['recommended_action']}"
                ]
            })
        else:
            overstocked = [p for p in products if p["days_stock_remaining"] > 5.0]
            top_overstock = overstocked[0] if overstocked else products[-1]
            actions.append({
                "priority": 3,
                "action_type": "PROMOTE",
                "product_name": top_overstock["product_name"],
                "headline": f"Bundle & Promote {top_overstock['product_name']}",
                "summary": f"Current stock covers {top_overstock['days_stock_remaining']} days of demand. Promote to free up working capital.",
                "estimated_impact": f"Unlock ₹{top_overstock['current_stock'] * top_overstock['unit_price']:.0f} Tied Working Capital",
                "evidence": [
                    f"Current stock level: {top_overstock['current_stock']} units",
                    f"Sales velocity: {top_overstock['avg_daily_demand']} units/day",
                    f"Excess inventory coverage: {top_overstock['days_stock_remaining']} days",
                    f"30-day product revenue: ₹{top_overstock['revenue_30d']:.0f}"
                ]
            })

        return actions[:3]

    def ask_merchant_advisor(self, query: str, db: Session, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Gathers factual backend metrics context and generates advice via Groq LLM or fallback interpreter.
        """
        kpis = analytics_service.get_dashboard_summary(db, store_id=store_id)
        products = analytics_service.get_product_intelligence(db, store_id=store_id)
        actions = self.get_what_to_do_today(db, store_id=store_id)

        # Context JSON passed strictly to LLM
        context_data = {
            "dashboard_kpis": kpis,
            "top_products": products[:5],
            "recommended_today_actions": actions
        }

        # Check if Groq client is available
        if llm_service.client:
            system_prompt = (
                "You are ShopWise AI Merchant Advisor — a concise, expert commerce intelligence assistant for local retail store owners in India.\n"
                "Answer the user's question using ONLY the provided factual business context.\n"
                "STRICT ROUTING & ADVICE RULES:\n"
                "1. Physical product restock questions (e.g., 'Why should I restock Amul Milk?') must ONLY reference physical inventory products (Amul Milk, Bread, Atta). NEVER suggest restocking payment gateways, software, or checkout services.\n"
                "2. Payment failure questions (e.g., 'Why are checkouts failing?') must ONLY reference payment gateway metrics (success rate %, checkout risk ₹, gateway retries).\n"
                "3. State clear evidence and exact figures (rupees ₹, units, growth %) from the context.\n"
                "4. Conclude with a direct 1-sentence actionable next step.\n"
                "5. Keep response friendly, structured, professional, and under 150 words."
            )
            user_message = (
                f"User Question: '{query}'\n\n"
                f"Factual Business Context:\n{json.dumps(context_data, indent=2)}"
            )

            try:
                response = llm_service.client.chat.completions.create(
                    model=settings.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=250,
                    temperature=0.2
                )
                advice_text = response.choices[0].message.content.strip()
                source = "groq_llm"
            except Exception as e:
                print(f"[Advisor] Groq API call failed: {e}")
                advice_text = self._fallback_advisor_reply(query, context_data)
                source = "fallback_deterministic"
        else:
            advice_text = self._fallback_advisor_reply(query, context_data)
            source = "fallback_deterministic"

        # Determine top recommended product (must be physical product)
        top_phys_prod = next((a["product_name"] for a in actions if a["action_type"] == "RESTOCK"), products[0]["product_name"] if products else "Amul Milk")

        return {
            "query": query,
            "advice": advice_text.replace("**", ""),
            "source": source,
            "context_metrics": {
                "revenue_today": kpis["revenue_today"],
                "revenue_7d": kpis["revenue_7d"],
                "total_revenue_at_risk_7d": kpis["total_revenue_at_risk_7d"],
                "top_recommended_product": top_phys_prod
            }
        }

    def _fallback_advisor_reply(self, query: str, context: Dict[str, Any]) -> str:
        q_lower = query.lower()
        actions = context.get("recommended_today_actions", [])
        products = context.get("top_products", [])
        kpis = context.get("dashboard_kpis", {})

        # Find specific product mentioned in query
        target_product = None
        for p in products:
            p_name = p.get("product_name", "")
            p_terms = p_name.lower().split()
            if any(term in q_lower for term in p_terms if len(term) > 3) or p_name.lower() in q_lower:
                target_product = p
                break

        # Case 1: Payment-related questions
        if any(w in q_lower for w in ["payment", "razorpay", "gateway", "failed checkout", "failure", "recovery"]):
            payment_action = next((a for a in actions if a.get("action_type") == "PAYMENT_RECOVERY"), None)
            if payment_action:
                return (
                    f"Payment Gateway Alert: {payment_action['summary']} "
                    f"Estimated revenue at risk: **{payment_action['estimated_impact']}**. "
                    f"Action: Activate Razorpay automated payment retry SMS & UPI intent fallback."
                )
            return (
                f"Payment gateway health is stable. Success rate is currently **{kpis.get('payment_success_rate', 100)}%** "
                f"with **{kpis.get('failed_orders_24h', 0)}** failed checkouts in 24h. Gateway operating within normal parameters."
            )

        # Case 2: Product / Restock / Inventory queries
        if any(w in q_lower for w in ["restock", "stock", "inventory", "stockout", "reorder", "supply", "why should i"]):
            if target_product:
                growth = target_product.get("demand_growth_pct", 0)
                days_left = target_product.get("days_stock_remaining", 0)
                risk_val = target_product.get("revenue_at_risk_7d", 0)
                stock_units = target_product.get("current_stock", 0)
                repurchase = target_product.get("repurchase_interval_days")
                rep_str = f" Repeat customers purchase every {repurchase} days." if repurchase else ""
                return (
                    f"You should restock **{target_product['product_name']}** because demand grew **{growth:+.1f}%** over the previous week. "
                    f"Current stock is **{stock_units} units** ({days_left} days remaining), putting **₹{risk_val:,.0f}** in 7-day revenue at risk.{rep_str} "
                    f"Action: Reorder today to avoid customer stockouts."
                )

            restock_action = next((a for a in actions if a.get("action_type") == "RESTOCK"), None)
            if restock_action:
                return (
                    f"Based on sales velocity, you should restock **{restock_action['product_name']}** immediately. "
                    f"{restock_action['summary']} Estimated impact: **{restock_action['estimated_impact']}**. "
                    f"Action: Reorder today to protect customer sales."
                )
            elif products:
                top_p = sorted(products, key=lambda x: x.get("days_stock_remaining", 999))[0]
                return (
                    f"Based on sales velocity, you should restock **{top_p['product_name']}** immediately. "
                    f"Current stock covers only **{top_p.get('days_stock_remaining', 0)} days** of demand with **₹{top_p.get('revenue_at_risk_7d', 0):,.0f}** revenue at risk. "
                    f"Action: Reorder today to avoid stockouts."
                )

        # Case 3: Revenue / Financial queries
        if any(w in q_lower for w in ["revenue", "money", "loss", "growth", "financial"]):
            return (
                f"Your store generated **₹{kpis.get('revenue_7d', 0):,.0f}** over the last 7 days from **{kpis.get('orders_30d', 0)}** orders. "
                f"However, you have **₹{kpis.get('total_revenue_at_risk_7d', 0):,.0f}** in 7-day stockout risk. "
                f"Action: Focus on restocking top-velocity items to protect revenue."
            )

        # Default fallback: return top physical product restock recommendation
        restock_act = next((a for a in actions if a.get("action_type") == "RESTOCK"), None)
        if restock_act:
            return (
                f"Here is your top physical inventory priority: **{restock_act['headline']}**. "
                f"{restock_act['summary']} Estimated impact: {restock_act['estimated_impact']}. "
                f"Action: Check inventory and place supplier replenishment orders."
            )

        top_act = actions[0] if actions else None
        if top_act:
            return (
                f"Here is your top priority for today: **{top_act['headline']}**. "
                f"{top_act['summary']} Estimated impact: {top_act['estimated_impact']}. "
                f"Action: Check merchant dashboard and take recommended action."
            )

        return "All key inventory items currently have sufficient stock coverage for projected demand."

merchant_advisor = MerchantAdvisorService()
