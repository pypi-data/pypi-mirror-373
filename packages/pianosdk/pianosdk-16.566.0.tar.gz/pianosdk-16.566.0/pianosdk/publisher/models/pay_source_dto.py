from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PaySourceDTO(BaseModel):
    id: Optional[int] = None
    identifier: Optional[str] = None
    caption: Optional[str] = None
    title: Optional[str] = None
    custom_title: Optional[str] = None


PaySourceDTO.model_rebuild()
