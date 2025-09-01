from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LocaleModel(BaseModel):
    locale: Optional[str] = None
    label: Optional[str] = None
    localized_label: Optional[str] = None
    is_default: Optional[bool] = None
    is_enabled: Optional[bool] = None
    is_rtl: Optional[bool] = None


LocaleModel.model_rebuild()
