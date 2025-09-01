from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ResourceStats(BaseModel):
    rid: Optional[str] = None
    num_bundles: Optional[int] = None
    num_customers: Optional[int] = None
    num_terms: Optional[int] = None
    tags: Optional[str] = None


ResourceStats.model_rebuild()
