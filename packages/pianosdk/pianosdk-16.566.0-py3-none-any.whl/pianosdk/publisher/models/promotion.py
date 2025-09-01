from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.promotion_fixed_discount import PromotionFixedDiscount
from typing import List


class Promotion(BaseModel):
    promotion_id: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    fixed_promotion_code: Optional[str] = None
    unlimited_uses: Optional[bool] = None
    promotion_code_prefix: Optional[str] = None
    new_customers_only: Optional[bool] = None
    discount_amount: Optional[float] = None
    discount_currency: Optional[str] = None
    discount: Optional[str] = None
    percentage_discount: Optional[float] = None
    discount_type: Optional[str] = None
    uses_allowed: Optional[int] = None
    uses: Optional[int] = None
    never_allow_zero: Optional[bool] = None
    term_dependency_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    create_date: Optional[datetime] = None
    create_by: Optional[str] = None
    update_date: Optional[datetime] = None
    update_by: Optional[str] = None
    deleted: Optional[bool] = None
    fixed_discount_list: Optional['List[PromotionFixedDiscount]'] = None
    apply_to_all_billing_periods: Optional[bool] = None
    can_be_applied_on_renewal: Optional[bool] = None
    billing_period_limit: Optional[int] = None


Promotion.model_rebuild()
