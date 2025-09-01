from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class VoucheringPolicy(BaseModel):
    vouchering_policy_id: Optional[str] = None
    vouchering_policy_billing_plan: Optional[str] = None
    vouchering_policy_billing_plan_description: Optional[str] = None
    vouchering_policy_redemption_url: Optional[str] = None


VoucheringPolicy.model_rebuild()
