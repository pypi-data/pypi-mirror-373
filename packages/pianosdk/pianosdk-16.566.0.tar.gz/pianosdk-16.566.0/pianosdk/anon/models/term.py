from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.resource import Resource


class Term(BaseModel):
    term_id: Optional[str] = None
    aid: Optional[str] = None
    resource: Optional['Resource'] = None
    type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    create_date: Optional[datetime] = None


Term.model_rebuild()
