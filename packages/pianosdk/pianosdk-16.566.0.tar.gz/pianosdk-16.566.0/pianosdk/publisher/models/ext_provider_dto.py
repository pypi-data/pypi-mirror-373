from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.external_api_field import ExternalAPIField
from pianosdk.publisher.models.external_api_property_schema import ExternalAPIPropertySchema
from typing import List


class ExtProviderDTO(BaseModel):
    name: Optional[str] = None
    properties: Optional['List[ExternalAPIPropertySchema]'] = None
    form_fields: Optional['List[ExternalAPIField]'] = None
    can_enforce_uniqueness: Optional[bool] = None
    enforce_uniqueness_by_default: Optional[bool] = None


ExtProviderDTO.model_rebuild()
