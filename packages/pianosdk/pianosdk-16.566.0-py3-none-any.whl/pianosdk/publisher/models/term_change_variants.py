from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.source_term_change_variants import SourceTermChangeVariants
from pianosdk.publisher.models.target_term_change_variants import TargetTermChangeVariants
from pianosdk.publisher.models.upgrade_offer_variant import UpgradeOfferVariant
from typing import List


class TermChangeVariants(BaseModel):
    source_term_change_variants: Optional['SourceTermChangeVariants'] = None
    target_term_change_variants: Optional['TargetTermChangeVariants'] = None
    upgrade_offer_variants: Optional['List[UpgradeOfferVariant]'] = None
    show_options: Optional[List[str]] = None


TermChangeVariants.model_rebuild()
