from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.linked_term_custom_data import LinkedTermCustomData


class LinkedTermConfigurationRequest(BaseModel):
    external_term_id: Optional[str] = None
    term_name: Optional[str] = None
    description: Optional[str] = None
    external_product_ids: Optional[str] = None
    subscription_management_url: Optional[str] = None
    custom_data: Optional['LinkedTermCustomData'] = None


LinkedTermConfigurationRequest.model_rebuild()
