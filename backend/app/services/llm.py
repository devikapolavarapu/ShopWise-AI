import os
import re
import json
from typing import Dict, Any, Optional
from app.config import settings
from app.schemas.entities import StructuredIntent, IntentParseResponse

class LLMService:
    def parse_intent(self, query: str) -> IntentParseResponse:
        raise NotImplementedError

    def explain_recommendation(self, store_name: str, score: float, evidence: list) -> str:
        raise NotImplementedError

class GroqLLMService(LLMService):
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                print("[LLMService] Groq client initialized successfully.")
            except Exception as e:
                print(f"[LLMService] Could not initialize Groq client: {e}")
                self.client = None

    def parse_intent(self, query: str) -> IntentParseResponse:
        if not self.client:
            print("[LLMService] GROQ_API_KEY missing or client unavailable. Using fallback regex intent parser.")
            return self._regex_fallback_intent(query, source="fallback_regex (No GROQ API Key)")

        system_prompt = (
            "You are a structured intent parser for a local shopping recommendation system in India. "
            "Convert the user's natural language search request into a JSON object matching this schema:\n"
            "{\n"
            '  "product": string (main target product name, e.g. "Amul milk", "bread"),\n'
            '  "category": string (e.g. "dairy", "bakery", "staples", "groceries"),\n'
            '  "max_price": float or null (maximum budget in rupees if specified, e.g. 70.0),\n'
            '  "radius_km": float or null (distance limit in km if specified, default 5.0),\n'
            '  "freshness_priority": string ("low", "medium", "high")\n'
            "}\n"
            "Return ONLY raw JSON, with no codeblocks, no extra markdown formatting, and no commentary."
        )

        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content.strip()
            data = json.loads(raw_content)

            intent = StructuredIntent(
                product=data.get("product", query),
                category=data.get("category", "groceries"),
                max_price=data.get("max_price"),
                radius_km=data.get("radius_km") or 5.0,
                freshness_priority=data.get("freshness_priority", "medium")
            )
            return IntentParseResponse(query=query, intent=intent, source="groq_llm")
        except Exception as e:
            print(f"[LLMService] Groq API call failed: {e}. Falling back to regex intent parser.")
            return self._regex_fallback_intent(query, source="fallback_regex (Groq Error)", error=str(e))

    def explain_recommendation(self, store_name: str, score: float, evidence: list) -> str:
        if not self.client:
            return f"{store_name} is recommended with a score of {score:.0f}/100 based on availability, proximity, and price."

        prompt = (
            f"Explain in 2 friendly sentences why {store_name} was selected as the best option. "
            f"Key evidence: {', '.join(evidence)}. Recommendation score: {score:.0f}/100."
        )

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return f"{store_name} is recommended with a overall score of {score:.0f}/100 based on: {', '.join(evidence)}."

    def _regex_fallback_intent(self, query: str, source: str, error: str = None) -> IntentParseResponse:
        """Deterministic keyword and regex intent parser fallback."""
        q_lower = query.lower()

        # Extract max price (e.g. "under 70 rupees", "under ₹70", "below 70")
        price_match = re.search(r'(?:under|below|less than|rs\.?|₹)\s*(\d+)', q_lower)
        max_price = float(price_match.group(1)) if price_match else None

        # Extract distance radius (e.g. "within 3 km", "under 5km")
        dist_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:km|kilometer)', q_lower)
        radius_km = float(dist_match.group(1)) if dist_match else 5.0

        # Freshness priority keyword check
        freshness_priority = "medium"
        if any(w in q_lower for w in ["fresh", "freshness", "latest", "today"]):
            freshness_priority = "high"

        # Product matching
        product = "Amul Milk"
        category = "Dairy"

        if "bread" in q_lower:
            product = "Britannia Bread"
            category = "Bakery"
        elif "atta" in q_lower or "wheat" in q_lower or "flour" in q_lower:
            product = "Aashirvaad Atta"
            category = "Staples"
        elif "paneer" in q_lower:
            product = "Mother Dairy Paneer"
            category = "Dairy"
        elif "salt" in q_lower:
            product = "Tata Salt"
            category = "Staples"
        elif "milk" in q_lower:
            product = "Amul Milk"
            category = "Dairy"

        intent = StructuredIntent(
            product=product,
            category=category,
            max_price=max_price,
            radius_km=radius_km,
            freshness_priority=freshness_priority
        )
        return IntentParseResponse(query=query, intent=intent, source=source, error=error)

# Singleton instance
llm_service = GroqLLMService()
