from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PerformanceMetricsDto(BaseModel):
    ga_account: Optional[str] = None
    is_enabled: Optional[str] = None
    track_only_aids: Optional[str] = None


PerformanceMetricsDto.model_rebuild()
