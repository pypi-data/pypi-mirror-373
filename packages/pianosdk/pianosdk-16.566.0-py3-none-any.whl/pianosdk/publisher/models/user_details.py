from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.price_dto import PriceDTO
from pianosdk.publisher.models.user_alias_dto import UserAliasDto
from typing import List


class UserDetails(BaseModel):
    uid: Optional[str] = None
    name: Optional[str] = None
    personal_name: Optional[str] = None
    display_name: Optional[str] = None
    image1: Optional[str] = None
    access_count: Optional[int] = None
    spent_money: Optional['List[PriceDTO]'] = None
    create_date: Optional[datetime] = None
    email: Optional[str] = None
    email_state: Optional[int] = None
    last_active_date: Optional[datetime] = None
    user_aliases: Optional['List[UserAliasDto]'] = None


UserDetails.model_rebuild()
