from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.user_info import UserInfo


class TemplateContext(BaseModel):
    user_info: Optional['UserInfo'] = None
    experience_id: Optional[str] = None
    experience_action_id: Optional[str] = None
    experience_execution_id: Optional[str] = None
    template_language: Optional[str] = None


TemplateContext.model_rebuild()
