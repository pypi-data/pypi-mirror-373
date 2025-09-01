from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.global_template_deployment_item import GlobalTemplateDeploymentItem
from typing import List


class GlobalTemplateDeployment(BaseModel):
    deployment_id: Optional[str] = None
    items: Optional['List[GlobalTemplateDeploymentItem]'] = None


GlobalTemplateDeployment.model_rebuild()
