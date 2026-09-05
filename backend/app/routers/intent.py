from fastapi import APIRouter
from app.schemas.entities import IntentParseRequest, IntentParseResponse
from app.services.llm import llm_service

router = APIRouter(prefix="/api", tags=["Intent"])

@router.post("/intent/parse", response_model=IntentParseResponse)
def parse_user_intent(request: IntentParseRequest):
    return llm_service.parse_intent(request.query)
