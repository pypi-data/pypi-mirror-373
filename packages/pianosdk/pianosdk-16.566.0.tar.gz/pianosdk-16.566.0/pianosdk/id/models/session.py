from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.geo_info import GeoInfo


class Session(BaseModel):
    aid: Optional[str] = None
    uid: Optional[str] = None
    jti: Optional[str] = None
    location: Optional['GeoInfo'] = None
    creation_date: Optional[int] = None
    last_activity_date: Optional[int] = None
    user_agent: Optional[str] = None
    trackable: Optional[bool] = None


Session.model_rebuild()
