from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import Any
from typing import Dict
from typing import List


class User(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    personal_name: Optional[str] = None
    uid: Optional[str] = None
    image1: Optional[str] = None
    create_date: Optional[datetime] = None
    reset_password_email_sent: Optional[bool] = None
    custom_fields: Optional['List[Dict[str, Any]]'] = None
    last_visit: Optional[datetime] = None
    last_login: Optional[datetime] = None
    display_name: Optional[str] = None


User.model_rebuild()
