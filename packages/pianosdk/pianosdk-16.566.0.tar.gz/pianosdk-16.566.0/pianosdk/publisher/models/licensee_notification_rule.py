from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class LicenseeNotificationRule(BaseModel):
    notification_rule_id: Optional[str] = None
    licensee_id: Optional[str] = None
    contract_id_list: Optional[List[str]] = None
    parameter: Optional[str] = None
    condition: Optional[str] = None
    condition_value: Optional[int] = None
    is_for_all_contracts: Optional[bool] = None


LicenseeNotificationRule.model_rebuild()
