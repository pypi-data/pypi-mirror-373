from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.country import Country
from pianosdk.publisher.models.term_brief import TermBrief
from typing import List


class DeliveryZone(BaseModel):
    delivery_zone_id: Optional[str] = None
    delivery_zone_name: Optional[str] = None
    countries: Optional['List[Country]'] = None
    terms: Optional['List[TermBrief]'] = None


DeliveryZone.model_rebuild()
