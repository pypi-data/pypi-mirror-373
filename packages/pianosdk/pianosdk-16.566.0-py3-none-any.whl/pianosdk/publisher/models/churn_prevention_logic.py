from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ChurnPreventionLogic(BaseModel):
    logic_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    default: Optional[bool] = None
    terms_count: Optional[int] = None
    scenarios: Optional[str] = None
    early_billing: Optional[str] = None


ChurnPreventionLogic.model_rebuild()
