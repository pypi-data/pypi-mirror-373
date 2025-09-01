from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class InitiateSecureFieldsParams(BaseModel):
    aid: Optional[str] = None
    tracking_id: Optional[str] = None
    authorization_amount: Optional[str] = None
    return_url: Optional[str] = None


InitiateSecureFieldsParams.model_rebuild()
