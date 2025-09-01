from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DeploymentApp(BaseModel):
    aid: Optional[str] = None
    name: Optional[str] = None
    app_logo: Optional[str] = None


DeploymentApp.model_rebuild()
