from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExternalAPIPropertySchema(BaseModel):
    field_name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    novalidate: Optional[bool] = None
    type: Optional[str] = None


ExternalAPIPropertySchema.model_rebuild()
