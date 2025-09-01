from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class OAuthToken(BaseModel):
    access_token: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None


OAuthToken.model_rebuild()
