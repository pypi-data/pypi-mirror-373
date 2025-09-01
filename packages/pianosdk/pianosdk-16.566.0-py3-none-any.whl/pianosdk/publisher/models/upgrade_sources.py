from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.source_eligible_term import SourceEligibleTerm
from pianosdk.publisher.models.source_ineligible_term import SourceIneligibleTerm
from typing import List


class UpgradeSources(BaseModel):
    eligible_options: Optional['List[SourceEligibleTerm]'] = None
    ineligible_options: Optional['List[SourceIneligibleTerm]'] = None


UpgradeSources.model_rebuild()
