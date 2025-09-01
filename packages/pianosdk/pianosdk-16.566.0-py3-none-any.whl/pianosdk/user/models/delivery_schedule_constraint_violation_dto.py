from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.user.models.period_reference_dto import PeriodReferenceDTO
from typing import List


class DeliveryScheduleConstraintViolationDTO(BaseModel):
    constraint_violation_code: Optional[str] = None
    target_period_reference: Optional['PeriodReferenceDTO'] = None
    conflicting_periods_references: Optional['List[PeriodReferenceDTO]'] = None
    message: Optional[str] = None


DeliveryScheduleConstraintViolationDTO.model_rebuild()
