from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import Dict
from typing import List


class PublisherRegisterRequest(BaseModel):
    aid: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    consents: Optional[str] = None
    custom_fields: Optional[str] = None
    form_id: Optional[str] = None
    phone: Optional[str] = None
    aliases: Optional[Dict[str, str]] = None
    phone_digital_code: Optional[str] = None
    passwordless: Optional[bool] = None
    confirmed_email: Optional[bool] = None
    magic_link_sent: Optional[bool] = None


PublisherRegisterRequest.model_rebuild()
