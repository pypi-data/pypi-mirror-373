from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class InstrumentDTO(BaseModel):
    require_3ds: Optional[bool] = None
    instrument_id: Optional[str] = None
    token: Optional[str] = None
    transaction_id: Optional[str] = None
    redirect_url: Optional[str] = None


InstrumentDTO.model_rebuild()
