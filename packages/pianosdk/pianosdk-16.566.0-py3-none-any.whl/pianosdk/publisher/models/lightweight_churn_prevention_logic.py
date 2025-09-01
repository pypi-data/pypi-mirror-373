from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LightweightChurnPreventionLogic(BaseModel):
    logic_id: Optional[str] = None
    name: Optional[str] = None
    default: Optional[bool] = None
    max_grace_period: Optional[int] = None


LightweightChurnPreventionLogic.model_rebuild()
