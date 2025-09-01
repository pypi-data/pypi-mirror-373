from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term_info import TermInfo
from typing import List


class UpgradeOption(BaseModel):
    id: Optional[str] = None
    term_from: Optional['TermInfo'] = None
    term_to: Optional['TermInfo'] = None
    bill_timing: Optional[str] = None
    prorate_access: Optional[bool] = None
    immediate_access: Optional[bool] = None
    show_option_in_channels: Optional[List[str]] = None


UpgradeOption.model_rebuild()
