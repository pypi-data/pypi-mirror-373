from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class NewscycleConfiguration(BaseModel):
    url: Optional[str] = None
    api_url: Optional[str] = None
    web_pages_url: Optional[str] = None
    site_id: Optional[str] = None
    synchronization_url: Optional[str] = None


NewscycleConfiguration.model_rebuild()
