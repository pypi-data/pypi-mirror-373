from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ReportResponse(BaseModel):
    error: Optional[str] = None
    message: Optional[str] = None
    report: Optional[str] = None


ReportResponse.model_rebuild()
