from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.custom_field_attribute_dto import CustomFieldAttributeDto
from pianosdk.id.models.tooltip import Tooltip
from pianosdk.id.models.validator import Validator
from typing import List


class CustomFieldDefinitionDto(BaseModel):
    field_name: Optional[str] = None
    title: Optional[str] = None
    comment: Optional[str] = None
    editable: Optional[bool] = None
    data_type: Optional[str] = None
    validators: Optional['List[Validator]'] = None
    options: Optional[List[str]] = None
    favourite_options: Optional[List[str]] = None
    options_link: Optional[int] = None
    set_name: Optional[str] = None
    required_by_default: Optional[bool] = None
    values_count: Optional[int] = None
    archived: Optional[bool] = None
    default_sort_order: Optional[int] = None
    attribute: Optional['CustomFieldAttributeDto'] = None
    tooltip: Optional['Tooltip'] = None
    parent: Optional[int] = None
    hidden: Optional[bool] = None


CustomFieldDefinitionDto.model_rebuild()
