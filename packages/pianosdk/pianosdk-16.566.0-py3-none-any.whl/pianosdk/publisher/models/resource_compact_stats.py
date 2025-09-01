from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ResourceCompactStats(BaseModel):
    rid: Optional[str] = None
    has_conversions: Optional[bool] = None
    num_terms: Optional[int] = None
    num_bundles: Optional[int] = None
    tags: Optional[str] = None


ResourceCompactStats.model_rebuild()
