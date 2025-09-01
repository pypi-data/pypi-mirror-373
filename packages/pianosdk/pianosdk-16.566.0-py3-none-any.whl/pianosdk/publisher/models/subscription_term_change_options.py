from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term_from import TermFrom
from pianosdk.publisher.models.term_to_eligible import TermToEligible
from pianosdk.publisher.models.term_to_ineligible import TermToIneligible
from pianosdk.publisher.models.term_to_upgrade_option import TermToUpgradeOption
from typing import List


class SubscriptionTermChangeOptions(BaseModel):
    change_from: Optional['TermFrom'] = None
    change_options: Optional['List[TermToUpgradeOption]'] = None
    eligible_options: Optional['List[TermToEligible]'] = None
    ineligible_options: Optional['List[TermToIneligible]'] = None


SubscriptionTermChangeOptions.model_rebuild()
