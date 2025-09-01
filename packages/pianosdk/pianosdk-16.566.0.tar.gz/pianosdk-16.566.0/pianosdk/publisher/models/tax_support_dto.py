from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TaxSupportDTO(BaseModel):
    caption: Optional[str] = None
    tax_format: Optional[str] = None


TaxSupportDTO.model_rebuild()
