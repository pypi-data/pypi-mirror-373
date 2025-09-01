from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.access import Access
from pianosdk.publisher.models.period import Period
from pianosdk.publisher.models.promo_code import PromoCode
from pianosdk.publisher.models.schedule import Schedule
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.term_conversion_subscription import TermConversionSubscription
from pianosdk.publisher.models.user_payment_dto import UserPaymentDTO
from pianosdk.publisher.models.user_payment_info import UserPaymentInfo


class TermConversionDTO(BaseModel):
    term_conversion_id: Optional[str] = None
    term: Optional['Term'] = None
    type: Optional[str] = None
    aid: Optional[str] = None
    user_access: Optional['Access'] = None
    user_payment: Optional['UserPaymentDTO'] = None
    create_date: Optional[datetime] = None
    browser_id: Optional[str] = None
    subscription: Optional['TermConversionSubscription'] = None
    promo_code: Optional['PromoCode'] = None
    user_payment_info: Optional['UserPaymentInfo'] = None
    schedule: Optional['Schedule'] = None
    period: Optional['Period'] = None


TermConversionDTO.model_rebuild()
