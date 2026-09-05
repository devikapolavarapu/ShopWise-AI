from app.services.llm import GroqLLMService

def test_regex_fallback_intent_parser():
    service = GroqLLMService()
    query = "Find me fresh Amul milk under 70 rupees within 3 km"
    resp = service._regex_fallback_intent(query, source="test")

    assert resp.intent.product == "Amul Milk"
    assert resp.intent.max_price == 70.0
    assert resp.intent.radius_km == 3.0
    assert resp.intent.freshness_priority == "high"
