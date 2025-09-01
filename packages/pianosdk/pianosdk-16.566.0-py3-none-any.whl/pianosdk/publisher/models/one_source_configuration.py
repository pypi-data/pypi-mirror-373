from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class OneSourceConfiguration(BaseModel):
    onesource_url: Optional[str] = None
    onesource_username: Optional[str] = None
    onesource_password: Optional[str] = None
    onesource_company_name: Optional[str] = None


OneSourceConfiguration.model_rebuild()
