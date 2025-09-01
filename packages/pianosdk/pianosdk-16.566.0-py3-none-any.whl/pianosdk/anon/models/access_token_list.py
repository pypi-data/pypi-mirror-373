from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AccessTokenList(BaseModel):
    value: Optional[str] = None
    cookie_domain: Optional[str] = None


AccessTokenList.model_rebuild()
