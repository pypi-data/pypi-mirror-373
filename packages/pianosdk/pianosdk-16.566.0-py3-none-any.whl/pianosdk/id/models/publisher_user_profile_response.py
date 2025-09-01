from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.publisher_custom_field_response import PublisherCustomFieldResponse
from typing import Dict
from typing import List


class PublisherUserProfileResponse(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    uid: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    create_date: Optional[int] = None
    reset_password_email_sent: Optional[bool] = None
    password: Optional[str] = None
    custom_fields: Optional['List[PublisherCustomFieldResponse]'] = None
    aliases: Optional[Dict[str, str]] = None


PublisherUserProfileResponse.model_rebuild()
