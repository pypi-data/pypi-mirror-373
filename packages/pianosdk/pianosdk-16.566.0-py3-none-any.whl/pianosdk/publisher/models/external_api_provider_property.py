from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExternalAPIProviderProperty(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None


ExternalAPIProviderProperty.model_rebuild()
