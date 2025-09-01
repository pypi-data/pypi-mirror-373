from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CyberSourceCaptureContextDto(BaseModel):
    capture_context: Optional[str] = None
    tracking_id: Optional[str] = None


CyberSourceCaptureContextDto.model_rebuild()
