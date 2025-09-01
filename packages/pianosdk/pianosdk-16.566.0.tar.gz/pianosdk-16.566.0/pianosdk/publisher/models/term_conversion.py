from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.access import Access
from pianosdk.publisher.models.period import Period
from pianosdk.publisher.models.promo_code import PromoCode
from pianosdk.publisher.models.schedule import Schedule
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.user_payment import UserPayment
from pianosdk.publisher.models.user_payment_info import UserPaymentInfo
from pianosdk.publisher.models.user_subscription import UserSubscription


class TermConversion(BaseModel):
    term_conversion_id: Optional[str] = None
    term: Optional['Term'] = None
    type: Optional[str] = None
    aid: Optional[str] = None
    user_access: Optional['Access'] = None
    user_payment: Optional['UserPayment'] = None
    create_date: Optional[datetime] = None
    browser_id: Optional[str] = None
    subscription: Optional['UserSubscription'] = None
    promo_code: Optional['PromoCode'] = None
    user_payment_info: Optional['UserPaymentInfo'] = None
    billing_plan: Optional[str] = None
    price_after_discount: Optional[str] = None
    price_after_discount_without_base: Optional[str] = None
    schedule: Optional['Schedule'] = None
    period: Optional['Period'] = None


TermConversion.model_rebuild()
