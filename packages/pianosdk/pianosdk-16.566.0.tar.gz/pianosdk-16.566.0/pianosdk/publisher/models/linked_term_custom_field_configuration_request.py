from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.linked_term_custom_field_params import LinkedTermCustomFieldParams
from typing import List


class LinkedTermCustomFieldConfigurationRequest(BaseModel):
    custom_fields: Optional['List[LinkedTermCustomFieldParams]'] = None


LinkedTermCustomFieldConfigurationRequest.model_rebuild()
