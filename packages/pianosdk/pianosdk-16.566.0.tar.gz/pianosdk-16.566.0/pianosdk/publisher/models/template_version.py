from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TemplateVersion(BaseModel):
    template_version_id: Optional[str] = None
    template_id: Optional[str] = None
    name: Optional[str] = None
    comment: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    html: Optional[str] = None
    css: Optional[str] = None
    version: Optional[int] = None
    lang: Optional[str] = None
    published: Optional[bool] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    xdays: Optional[int] = None


TemplateVersion.model_rebuild()
