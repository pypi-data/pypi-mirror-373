from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.consent_model import ConsentModel
from pianosdk.id.models.custom_field_value_dto import CustomFieldValueDto
from typing import Dict
from typing import List


class SocialAdditionalInputRequest(BaseModel):
    additional_input_state: Optional[str] = None
    consents: Optional['List[ConsentModel]'] = None
    custom_field_values: Optional['List[CustomFieldValueDto]'] = None
    email: Optional[str] = None
    aliases: Optional[Dict[str, str]] = None


SocialAdditionalInputRequest.model_rebuild()
