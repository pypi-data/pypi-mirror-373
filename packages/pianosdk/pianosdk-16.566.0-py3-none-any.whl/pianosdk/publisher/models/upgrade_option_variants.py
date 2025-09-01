from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.upgrade_options_variant import UpgradeOptionsVariant
from typing import List


class UpgradeOptionVariants(BaseModel):
    eligible_options: Optional['List[UpgradeOptionsVariant]'] = None
    ineligible_options: Optional['List[UpgradeOptionsVariant]'] = None


UpgradeOptionVariants.model_rebuild()
