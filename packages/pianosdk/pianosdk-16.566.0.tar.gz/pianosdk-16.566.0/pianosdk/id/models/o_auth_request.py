from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class OAuthRequest(BaseModel):
    client_id: Optional[str] = None
    refresh_token: Optional[str] = None
    grant_type: Optional[str] = None
    code: Optional[str] = None
    client_secret: Optional[str] = None
    redirect_uri: Optional[str] = None
    code_verifier: Optional[str] = None


OAuthRequest.model_rebuild()
