from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App
from pianosdk.publisher.models.external_api_field import ExternalAPIField
from pianosdk.publisher.models.external_api_provider_property import ExternalAPIProviderProperty
from pianosdk.publisher.models.term import Term
from typing import List


class ExternalAPIConfiguration(BaseModel):
    external_api_id: Optional[str] = None
    name: Optional[str] = None
    app: Optional['App'] = None
    form_fields: Optional['List[ExternalAPIField]'] = None
    properties: Optional['List[ExternalAPIProviderProperty]'] = None
    provider: Optional[str] = None
    description: Optional[str] = None
    terms: Optional['List[Term]'] = None
    enforce_uniqueness: Optional[bool] = None
    can_update_fields: Optional[bool] = None
    force_grace_period: Optional[int] = None
    external_api_source_id: Optional[int] = None
    default_verification_period: Optional[int] = None


ExternalAPIConfiguration.model_rebuild()
