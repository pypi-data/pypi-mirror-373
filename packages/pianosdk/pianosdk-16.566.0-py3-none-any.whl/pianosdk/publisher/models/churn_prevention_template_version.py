from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ChurnPreventionTemplateVersion(BaseModel):
    template_id: Optional[str] = None
    version_id: Optional[int] = None
    version: Optional[int] = None
    name: Optional[str] = None


ChurnPreventionTemplateVersion.model_rebuild()
