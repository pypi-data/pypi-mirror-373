from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App
from pianosdk.publisher.models.inquiry_comment import InquiryComment
from pianosdk.publisher.models.resource import Resource
from pianosdk.publisher.models.user import User
from typing import List


class PaymentInquiry(BaseModel):
    payment_inquiry_id: Optional[str] = None
    resource: Optional['Resource'] = None
    app: Optional['App'] = None
    state: Optional[int] = None
    inquiry_reason: Optional[str] = None
    create_date: Optional[str] = None
    inquiry_comments: Optional['List[InquiryComment]'] = None
    category: Optional[str] = None
    update_state_by: Optional['User'] = None
    update_state_date: Optional[str] = None
    start_date: Optional[str] = None
    expire_date: Optional[str] = None
    transaction_date: Optional[str] = None
    transaction_id: Optional[str] = None
    spent_money: Optional[float] = None
    spent_money_display: Optional[str] = None
    source: Optional[str] = None
    currency: Optional[str] = None
    refunded_date: Optional[str] = None
    is_access_expired: Optional[bool] = None
    is_access_revoked: Optional[bool] = None
    is_access_unlimited: Optional[bool] = None
    refund_amount: Optional[str] = None
    refund_amount_recalculated: Optional[bool] = None


PaymentInquiry.model_rebuild()
