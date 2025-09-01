from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.schedule_period import SchedulePeriod
from typing import List


class Contract(BaseModel):
    contract_id: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    create_date: Optional[datetime] = None
    landing_page_url: Optional[str] = None
    licensee_id: Optional[str] = None
    seats_number: Optional[int] = None
    is_hard_seats_limit_type: Optional[bool] = None
    rid: Optional[str] = None
    schedule_id: Optional[str] = None
    contract_is_active: Optional[bool] = None
    contract_type: Optional[str] = None
    contract_conversions_count: Optional[int] = None
    contract_periods: Optional['List[SchedulePeriod]'] = None


Contract.model_rebuild()
