from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.user_model import UserModel


class UserInfo(BaseModel):
    user_lang: Optional[str] = None
    is_new_customer: Optional[bool] = None
    user: Optional['UserModel'] = None
    country_code: Optional[str] = None
    postal_code: Optional[str] = None
    tax_support: Optional[str] = None


UserInfo.model_rebuild()
