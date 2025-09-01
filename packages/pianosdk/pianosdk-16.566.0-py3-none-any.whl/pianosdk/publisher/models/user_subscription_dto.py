from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserSubscriptionDto(BaseModel):
    term_name: Optional[str] = None
    term_id: Optional[str] = None
    type: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    billing_plan: Optional[str] = None
    image_url: Optional[str] = None
    resource_name: Optional[str] = None
    rid: Optional[str] = None
    next_bill_date: Optional[str] = None
    subscription_last_payment: Optional[str] = None
    status: Optional[str] = None
    status_label: Optional[str] = None
    creadit_card_expire: Optional[str] = None
    creadit_card_expire_soon: Optional[bool] = None
    subscription_id: Optional[str] = None
    payment_method: Optional[str] = None
    access_expired: Optional[bool] = None
    in_app_payment: Optional[bool] = None
    psc_subscriber_number: Optional[str] = None
    conversion_result: Optional[str] = None
    external_api_name: Optional[str] = None
    charge_count: Optional[int] = None
    status_display: Optional[str] = None
    auto_renew: Optional[bool] = None
    user_payment_info_id: Optional[str] = None
    access_id: Optional[str] = None
    last_conversion_id: Optional[str] = None
    last_payment_conversion_id: Optional[str] = None
    delivery_schedule_pub_id: Optional[str] = None


UserSubscriptionDto.model_rebuild()
