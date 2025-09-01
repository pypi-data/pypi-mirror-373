from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.deployment_app_details import DeploymentAppDetails
from pianosdk.publisher.models.user import User
from typing import List


class DeploymentDetails(BaseModel):
    deployment_id: Optional[str] = None
    status: Optional[str] = None
    offer_template_id: Optional[str] = None
    offer_template_name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[int] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    applications: Optional['List[DeploymentAppDetails]'] = None


DeploymentDetails.model_rebuild()
