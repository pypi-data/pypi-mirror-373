from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class StripeProperties(BaseModel):
    public_key: Optional[str] = None
    account_id: Optional[str] = None
    zip_is_hidden: Optional[bool] = None
    collect_cardholder_name: Optional[bool] = None


StripeProperties.model_rebuild()
