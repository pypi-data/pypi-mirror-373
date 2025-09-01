from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ConversionValueDTO(BaseModel):
    currency: Optional[str] = None
    conversion_category: Optional[str] = None
    value: Optional[float] = None


ConversionValueDTO.model_rebuild()
