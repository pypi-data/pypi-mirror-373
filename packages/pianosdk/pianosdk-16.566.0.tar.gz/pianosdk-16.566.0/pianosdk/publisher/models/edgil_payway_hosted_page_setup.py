from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EdgilPaywayHostedPageSetup(BaseModel):
    request_id: Optional[str] = None
    reply_url: Optional[str] = None
    action_url: Optional[str] = None


EdgilPaywayHostedPageSetup.model_rebuild()
