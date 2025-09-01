from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Consent(BaseModel):
    consent_id: Optional[str] = None
    field_name: Optional[str] = None
    field_id: Optional[str] = None
    display_text: Optional[str] = None
    error_message: Optional[str] = None
    type: Optional[str] = None
    pre_checked: Optional[bool] = None
    required: Optional[bool] = None
    enabled: Optional[bool] = None
    field_id_enabled: Optional[bool] = None


Consent.model_rebuild()
