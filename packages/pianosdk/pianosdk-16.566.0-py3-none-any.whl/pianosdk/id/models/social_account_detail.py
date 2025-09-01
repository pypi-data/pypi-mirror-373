from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SocialAccountDetail(BaseModel):
    provider_name: Optional[str] = None
    provider_user_id: Optional[str] = None
    user_email: Optional[str] = None


SocialAccountDetail.model_rebuild()
