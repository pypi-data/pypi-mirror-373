from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseTransaction(BaseModel):
    tracking_id: Optional[str] = None
    sender_email: Optional[str] = None


EraseTransaction.model_rebuild()
