from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.deployment_app import DeploymentApp
from pianosdk.publisher.models.user import User
from typing import List


class DeploymentListItem(BaseModel):
    deployment_id: Optional[str] = None
    global_template_version: Optional[int] = None
    deployment_date: Optional[datetime] = None
    user: Optional['User'] = None
    status: Optional[str] = None
    applications: Optional['List[DeploymentApp]'] = None


DeploymentListItem.model_rebuild()
