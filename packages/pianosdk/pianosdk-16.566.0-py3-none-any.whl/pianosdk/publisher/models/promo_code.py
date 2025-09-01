from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class PromoCode(BaseModel):
    promo_code_id: Optional[str] = None
    promotion_id: Optional[str] = None
    code: Optional[str] = None
    assigned_email: Optional[str] = None
    reserve_date: Optional[datetime] = None
    state: Optional[str] = None
    state_value: Optional[str] = None
    claimed_user: Optional['User'] = None
    claimed_date: Optional[datetime] = None
    create_date: Optional[datetime] = None
    create_by: Optional[str] = None
    update_date: Optional[datetime] = None
    update_by: Optional[str] = None
    deleted: Optional[bool] = None
    last_original_price: Optional[str] = None


PromoCode.model_rebuild()
