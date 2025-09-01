from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ZuoraConfiguration(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    entity_name: Optional[str] = None
    entity_id: Optional[str] = None


ZuoraConfiguration.model_rebuild()
