from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SharedAccountParam(BaseModel):
    account_id: Optional[str] = None
    user_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None
    redeemed: Optional[datetime] = None
    active: Optional[bool] = None


SharedAccountParam.model_rebuild()
