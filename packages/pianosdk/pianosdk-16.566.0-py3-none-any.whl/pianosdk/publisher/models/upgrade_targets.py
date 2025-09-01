from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.target_eligible_term import TargetEligibleTerm
from pianosdk.publisher.models.target_ineligible_term import TargetIneligibleTerm
from pianosdk.publisher.models.target_upgrade_option import TargetUpgradeOption
from typing import List


class UpgradeTargets(BaseModel):
    already_configured_options: Optional['List[TargetUpgradeOption]'] = None
    eligible_options: Optional['List[TargetEligibleTerm]'] = None
    ineligible_options: Optional['List[TargetIneligibleTerm]'] = None


UpgradeTargets.model_rebuild()
