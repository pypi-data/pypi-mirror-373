from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.source_term_change_variant import SourceTermChangeVariant
from typing import List


class SourceTermChangeVariants(BaseModel):
    term_and_periods: Optional['List[SourceTermChangeVariant]'] = None


SourceTermChangeVariants.model_rebuild()
