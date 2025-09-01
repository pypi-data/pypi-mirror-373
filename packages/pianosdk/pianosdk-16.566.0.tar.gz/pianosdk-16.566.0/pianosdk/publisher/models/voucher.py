from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user_address import UserAddress


class Voucher(BaseModel):
    pub_id: Optional[str] = None
    code: Optional[str] = None
    state: Optional[str] = None
    state_label: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_message: Optional[str] = None
    send_date: Optional[datetime] = None
    create_date: Optional[datetime] = None
    expires: Optional[str] = None
    expire_date: Optional[datetime] = None
    redeemed: Optional[datetime] = None
    revoke_date: Optional[datetime] = None
    period: Optional[str] = None
    app_name: Optional[str] = None
    term_name: Optional[str] = None
    term_type: Optional[str] = None
    term_id: Optional[str] = None
    resource_name: Optional[str] = None
    price: Optional[str] = None
    transaction_id: Optional[str] = None
    is_revocable: Optional[bool] = None
    is_refundable: Optional[bool] = None
    is_resendable: Optional[bool] = None
    refund_amount: Optional[str] = None
    refund_amount_recalculated: Optional[bool] = None
    user_address: Optional['UserAddress'] = None


Voucher.model_rebuild()
