from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class SocialLinkingResponse(BaseModel):
    identity_social_linking_state: Optional[str] = None
    password_confirmation_available: Optional[bool] = None
    linked_social_accounts: Optional[List[str]] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    social_type: Optional[str] = None
    is_passwordless: Optional[bool] = None


SocialLinkingResponse.model_rebuild()
