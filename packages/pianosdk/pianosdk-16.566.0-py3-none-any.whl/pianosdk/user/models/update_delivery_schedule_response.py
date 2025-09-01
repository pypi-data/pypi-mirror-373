from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.user.models.delivery_schedule_constraint_violations_dto import DeliveryScheduleConstraintViolationsDTO


class UpdateDeliveryScheduleResponse(BaseModel):
    constraint_violations: Optional['DeliveryScheduleConstraintViolationsDTO'] = None


UpdateDeliveryScheduleResponse.model_rebuild()
