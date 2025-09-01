from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.show_option_in_channel_stats import ShowOptionInChannelStats
from typing import List


class ShowOptionInCounters(BaseModel):
    selected_channel: Optional[str] = None
    show_option_in_channels: Optional['List[ShowOptionInChannelStats]'] = None


ShowOptionInCounters.model_rebuild()
