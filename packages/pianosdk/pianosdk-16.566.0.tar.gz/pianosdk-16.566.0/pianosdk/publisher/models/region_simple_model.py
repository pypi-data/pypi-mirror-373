from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class RegionSimpleModel(BaseModel):
    region_name: Optional[str] = None
    pub_id: Optional[str] = None


RegionSimpleModel.model_rebuild()
