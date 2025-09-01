from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import Any
from typing import List


class BillingPlanTable(BaseModel):
    payment_billing_plan_table: Optional['List[Any]'] = None


BillingPlanTable.model_rebuild()
