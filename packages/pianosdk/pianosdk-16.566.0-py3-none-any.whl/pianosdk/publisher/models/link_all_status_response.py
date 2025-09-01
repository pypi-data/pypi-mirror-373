from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkAllStatusResponse(BaseModel):
    task_id: Optional[str] = None
    status: Optional[str] = None
    fail_message: Optional[str] = None


LinkAllStatusResponse.model_rebuild()
