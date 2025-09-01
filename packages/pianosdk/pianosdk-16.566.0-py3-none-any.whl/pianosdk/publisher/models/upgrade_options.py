from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.page_info import PageInfo
from pianosdk.publisher.models.show_option_in_counters import ShowOptionInCounters
from pianosdk.publisher.models.upgrade_option import UpgradeOption
from typing import List


class UpgradeOptions(BaseModel):
    page_info: Optional['PageInfo'] = None
    upgrade_options: Optional['List[UpgradeOption]'] = None
    show_option_in_counters: Optional['ShowOptionInCounters'] = None


UpgradeOptions.model_rebuild()
