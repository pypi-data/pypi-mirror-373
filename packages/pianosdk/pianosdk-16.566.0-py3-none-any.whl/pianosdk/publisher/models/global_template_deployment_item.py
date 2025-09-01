from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class GlobalTemplateDeploymentItem(BaseModel):
    item_id: Optional[str] = None
    template_id: Optional[str] = None
    aid: Optional[str] = None
    status: Optional[str] = None


GlobalTemplateDeploymentItem.model_rebuild()
