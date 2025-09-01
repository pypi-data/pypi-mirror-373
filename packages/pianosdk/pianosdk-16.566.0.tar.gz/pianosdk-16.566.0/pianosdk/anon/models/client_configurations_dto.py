from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ClientConfigurationsDto(BaseModel):
    ga_account: Optional[str] = None
    is_performance_metrics_enabled: Optional[str] = None
    performance_metrics_ga_account: Optional[str] = None
    performance_metrics_track_only_aids: Optional[str] = None
    msqa_client_id: Optional[str] = None


ClientConfigurationsDto.model_rebuild()
