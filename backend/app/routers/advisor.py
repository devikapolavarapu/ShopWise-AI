from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.advisor import merchant_advisor

router = APIRouter(prefix="/api", tags=["AI Merchant Advisor"])

class AdvisorQueryRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "What should I restock today?"})
    store_id: Optional[int] = None

@router.post("/advisor/query")
def ask_advisor(request: AdvisorQueryRequest, db: Session = Depends(get_db)):
    return merchant_advisor.ask_merchant_advisor(query=request.query, db=db, store_id=request.store_id)
