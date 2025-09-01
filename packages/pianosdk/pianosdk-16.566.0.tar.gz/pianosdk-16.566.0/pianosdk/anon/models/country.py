from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.region import Region
from typing import List


class Country(BaseModel):
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    country_id: Optional[str] = None
    regions: Optional['List[Region]'] = None


Country.model_rebuild()
