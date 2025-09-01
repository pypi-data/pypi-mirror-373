from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExternalCss(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    status: Optional[str] = None
    position: Optional[int] = None
    external_css_id: Optional[str] = None


ExternalCss.model_rebuild()
