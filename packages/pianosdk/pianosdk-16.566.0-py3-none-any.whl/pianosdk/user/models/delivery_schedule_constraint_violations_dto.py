from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.user.models.delivery_schedule_constraint_violation_dto import DeliveryScheduleConstraintViolationDTO
from typing import List


class DeliveryScheduleConstraintViolationsDTO(BaseModel):
    constraint_violations: Optional['List[DeliveryScheduleConstraintViolationDTO]'] = None


DeliveryScheduleConstraintViolationsDTO.model_rebuild()
