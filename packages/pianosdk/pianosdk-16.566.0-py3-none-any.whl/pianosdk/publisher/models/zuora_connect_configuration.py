from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ZuoraConnectConfiguration(BaseModel):
    email: Optional[str] = None
    zuora_api_token: Optional[str] = None


ZuoraConnectConfiguration.model_rebuild()
