from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Email(BaseModel):
    email_id: Optional[int] = None
    name: Optional[str] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    publisher_config: Optional[str] = None
    default_template_id: Optional[str] = None


Email.model_rebuild()
