from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PeriodReferenceDTO(BaseModel):
    period_pub_id: Optional[str] = None
    index_in_array: Optional[int] = None


PeriodReferenceDTO.model_rebuild()
