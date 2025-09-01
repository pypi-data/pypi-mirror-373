from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PublicCaptchaConfig(BaseModel):
    aid: Optional[str] = None
    enabled: Optional[bool] = None
    captcha3_site_key: Optional[str] = None


PublicCaptchaConfig.model_rebuild()
