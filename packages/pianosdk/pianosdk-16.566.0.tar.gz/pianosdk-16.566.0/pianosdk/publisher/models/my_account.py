from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class MyAccount(BaseModel):
    enabled: Optional[bool] = None


MyAccount.model_rebuild()
