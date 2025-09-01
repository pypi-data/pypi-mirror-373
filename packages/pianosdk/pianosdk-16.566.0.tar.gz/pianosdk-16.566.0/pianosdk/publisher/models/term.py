from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.country import Country
from pianosdk.publisher.models.delivery_zone import DeliveryZone
from pianosdk.publisher.models.external_api_field import ExternalAPIField
from pianosdk.publisher.models.resource import Resource
from pianosdk.publisher.models.schedule import Schedule
from pianosdk.publisher.models.term_change_option import TermChangeOption
from pianosdk.publisher.models.vouchering_policy import VoucheringPolicy
from typing import Any
from typing import Dict
from typing import List


class Term(BaseModel):
    term_id: Optional[str] = None
    aid: Optional[str] = None
    resource: Optional['Resource'] = None
    type: Optional[str] = None
    type_name: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    product_category: Optional[str] = None
    verify_on_renewal: Optional[bool] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    term_billing_descriptor: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    payment_billing_plan_description: Optional[str] = None
    payment_billing_plan_table: Optional['List[Any]'] = None
    payment_allow_renew_days: Optional[int] = None
    payment_force_auto_renew: Optional[bool] = None
    payment_is_custom_price_available: Optional[bool] = None
    payment_is_subscription: Optional[bool] = None
    payment_has_free_trial: Optional[bool] = None
    payment_new_customers_only: Optional[bool] = None
    payment_trial_new_customers_only: Optional[bool] = None
    payment_allow_promo_codes: Optional[bool] = None
    payment_renew_grace_period: Optional[int] = None
    payment_allow_gift: Optional[bool] = None
    payment_currency: Optional[str] = None
    currency_symbol: Optional[str] = None
    payment_first_price: Optional[float] = None
    schedule: Optional['Schedule'] = None
    schedule_billing: Optional[str] = None
    custom_require_user: Optional[bool] = None
    custom_default_access_period: Optional[int] = None
    adview_vast_url: Optional[str] = None
    adview_access_period: Optional[int] = None
    registration_access_period: Optional[int] = None
    registration_grace_period: Optional[int] = None
    external_api_id: Optional[str] = None
    external_api_name: Optional[str] = None
    external_api_source: Optional[int] = None
    external_api_form_fields: Optional['List[ExternalAPIField]'] = None
    evt_verification_period: Optional[int] = None
    evt_fixed_time_access_period: Optional[int] = None
    evt_grace_period: Optional[int] = None
    evt_itunes_bundle_id: Optional[str] = None
    evt_itunes_product_id: Optional[str] = None
    evt_google_play_product_id: Optional[str] = None
    evt_cds_product_id: Optional[str] = None
    evt: Optional['Term'] = None
    collect_address: Optional[bool] = None
    delivery_zone: Optional['List[DeliveryZone]'] = None
    default_country: Optional['Country'] = None
    vouchering_policy: Optional['VoucheringPolicy'] = None
    billing_config: Optional[str] = None
    is_allowed_to_change_schedule_period_in_past: Optional[bool] = None
    collect_shipping_address: Optional[bool] = None
    change_options: Optional['List[TermChangeOption]'] = None
    shared_account_count: Optional[int] = None
    shared_redemption_url: Optional[str] = None
    billing_configuration: Optional[str] = None
    show_full_billing_plan: Optional[bool] = None
    external_term_id: Optional[str] = None
    external_product_ids: Optional[str] = None
    subscription_management_url: Optional[str] = None
    custom_data: Optional['Dict[str, Any]'] = None
    allow_start_in_future: Optional[bool] = None
    maximum_days_in_advance: Optional[int] = None


Term.model_rebuild()
