from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Mail(BaseModel):
    email_subject: Optional[str] = None
    email_body: Optional[str] = None


Mail.model_rebuild()
