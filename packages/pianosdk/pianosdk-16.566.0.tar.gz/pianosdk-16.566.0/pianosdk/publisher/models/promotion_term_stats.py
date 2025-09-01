from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.price_dto import PriceDTO
from typing import List


class PromotionTermStats(BaseModel):
    pub_id: Optional[str] = None
    term_pub_id: Optional[str] = None
    total_sales: Optional['List[PriceDTO]'] = None
    conversion: Optional[int] = None


PromotionTermStats.model_rebuild()
