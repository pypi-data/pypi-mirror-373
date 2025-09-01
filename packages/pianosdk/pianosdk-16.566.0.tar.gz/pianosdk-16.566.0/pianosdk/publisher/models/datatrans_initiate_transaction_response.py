from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DatatransInitiateTransactionResponse(BaseModel):
    transaction_id: Optional[str] = None


DatatransInitiateTransactionResponse.model_rebuild()
