from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.experience import Experience
from pianosdk.publisher.models.money import Money
from typing import List


class ExperienceStat(BaseModel):
    experience: Optional['Experience'] = None
    conversion_count: Optional[int] = None
    net_revenues: Optional['List[Money]'] = None


ExperienceStat.model_rebuild()
