from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.deployment_content_fields import DeploymentContentFields
from typing import List


class DeploymentVariantParamDto(BaseModel):
    offer_template_variant_id: Optional[str] = None
    name: Optional[str] = None
    content_field_list: Optional['List[DeploymentContentFields]'] = None


DeploymentVariantParamDto.model_rebuild()
