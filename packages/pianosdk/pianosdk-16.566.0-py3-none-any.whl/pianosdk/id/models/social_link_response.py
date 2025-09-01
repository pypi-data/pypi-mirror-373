from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SocialLinkResponse(BaseModel):
    uri: Optional[str] = None


SocialLinkResponse.model_rebuild()
