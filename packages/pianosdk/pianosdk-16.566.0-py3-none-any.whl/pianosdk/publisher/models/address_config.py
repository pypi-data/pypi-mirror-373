from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AddressConfig(BaseModel):
    selected: Optional[bool] = None
    selected_by_default: Optional[bool] = None
    address_field: Optional[str] = None
    required: Optional[bool] = None
    default_value: Optional[str] = None
    field: Optional[str] = None


AddressConfig.model_rebuild()
