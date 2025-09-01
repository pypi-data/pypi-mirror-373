from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.price_dto import PriceDTO
from pianosdk.publisher.models.user_alias_dto import UserAliasDto
from typing import List


class UserInfo(BaseModel):
    name: Optional[str] = None
    personal_name: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    display_name: Optional[str] = None
    uid: Optional[str] = None
    image1: Optional[str] = None
    create_date: Optional[str] = None
    access_count: Optional[int] = None
    next_bill: Optional[str] = None
    spent_money: Optional['List[PriceDTO]'] = None
    has_trial: Optional[bool] = None
    last_unresolved_inquiry_id: Optional[str] = None
    last_issue_id: Optional[str] = None
    last_comment: Optional[str] = None
    email: Optional[str] = None
    last_visit: Optional[datetime] = None
    user_aliases: Optional['List[UserAliasDto]'] = None
    email_state: Optional[int] = None


UserInfo.model_rebuild()
