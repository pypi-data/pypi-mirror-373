from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class RedemptionPage(BaseModel):
    enabled: Optional[bool] = None


RedemptionPage.model_rebuild()
