from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LicenseeNotification(BaseModel):
    notification_id: Optional[str] = None
    licensee_id: Optional[str] = None
    contract_id: Optional[str] = None
    message: Optional[str] = None
    parameter: Optional[str] = None
    condition: Optional[str] = None
    condition_value: Optional[int] = None
    create_date: Optional[datetime] = None


LicenseeNotification.model_rebuild()
