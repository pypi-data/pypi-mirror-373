from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.pay_source_dto import PaySourceDTO
from pianosdk.publisher.models.user import User
from typing import List


class CheckoutFlow(BaseModel):
    checkout_flow_id: Optional[str] = None
    name: Optional[str] = None
    checkout_flow_type: Optional[str] = None
    description: Optional[str] = None
    create_date: Optional[datetime] = None
    create_by: Optional['User'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    is_passwordless: Optional[bool] = None
    is_single_step_enabled: Optional[bool] = None
    is_auto_detect_email: Optional[bool] = None
    is_custom_checkout_modules_enabled: Optional[bool] = None
    deleted: Optional[bool] = None
    pay_sources: Optional['List[PaySourceDTO]'] = None
    inline_checkout_modules: Optional[List[str]] = None
    modal_checkout_modules: Optional[List[str]] = None


CheckoutFlow.model_rebuild()
