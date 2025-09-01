from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TemplateConfig(BaseModel):
    name: Optional[str] = None
    content1_type: Optional[str] = None
    content2_type: Optional[str] = None
    content3_type: Optional[str] = None
    content1_value: Optional[str] = None
    content2_value: Optional[str] = None
    content3_value: Optional[str] = None
    history_list: Optional[str] = None
    template_type: Optional[str] = None
    boilerplate_type: Optional[str] = None


TemplateConfig.model_rebuild()
