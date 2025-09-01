from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.deployment_content_fields import DeploymentContentFields
from pianosdk.publisher.models.deployment_variant_param_dto import DeploymentVariantParamDto
from pianosdk.publisher.models.user import User
from typing import List


class DeploymentAppDetails(BaseModel):
    item_id: Optional[str] = None
    status: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    app_logo: Optional[str] = None
    offer_template_id: Optional[str] = None
    offer_template_name: Optional[str] = None
    version: Optional[int] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    content_field_list: Optional['List[DeploymentContentFields]'] = None
    variant_list: Optional['List[DeploymentVariantParamDto]'] = None
    selected: Optional[str] = None


DeploymentAppDetails.model_rebuild()
