from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BraintreeMerchantAccountIdEntry(BaseModel):
    currency: Optional[str] = None
    merchant_account_id: Optional[str] = None


BraintreeMerchantAccountIdEntry.model_rebuild()
