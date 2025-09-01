from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class GlobalTemplateRecentDeployments(BaseModel):
    new_inherited_templates_count: Optional[int] = None
    new_content_fields_count: Optional[int] = None


GlobalTemplateRecentDeployments.model_rebuild()
