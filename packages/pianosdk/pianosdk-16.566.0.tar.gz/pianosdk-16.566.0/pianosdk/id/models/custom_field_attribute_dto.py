from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class CustomFieldAttributeDto(BaseModel):
    date_format: Optional[str] = None
    autofill: Optional[bool] = None
    default: Optional[bool] = None
    dmp_segmentation_enable: Optional[bool] = None
    multiline: Optional[bool] = None
    default_value: Optional[str] = None
    placeholder: Optional[str] = None
    pre_select_country_by_ip: Optional[bool] = None
    _global: Optional[bool] = None
    global_status: Optional[str] = None
    aid_list: Optional[List[str]] = None
    linked_term_field: Optional[bool] = None


CustomFieldAttributeDto.model_rebuild()
