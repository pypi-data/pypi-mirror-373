from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DeploymentContentFields(BaseModel):
    name: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None


DeploymentContentFields.model_rebuild()
