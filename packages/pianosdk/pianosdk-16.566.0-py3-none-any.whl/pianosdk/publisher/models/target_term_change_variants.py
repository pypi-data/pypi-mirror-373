from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.target_term_change_variant import TargetTermChangeVariant
from typing import List


class TargetTermChangeVariants(BaseModel):
    eligible_options: Optional['List[TargetTermChangeVariant]'] = None
    ineligible_options: Optional['List[TargetTermChangeVariant]'] = None


TargetTermChangeVariants.model_rebuild()
