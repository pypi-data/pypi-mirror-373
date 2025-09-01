from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class CheckoutFlowLightModel(BaseModel):
    checkout_flow_id: Optional[str] = None
    name: Optional[str] = None
    checkout_flow_type: Optional[str] = None
    description: Optional[str] = None
    create_date: Optional[datetime] = None
    create_by: Optional['User'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    is_passwordless: Optional[bool] = None


CheckoutFlowLightModel.model_rebuild()
