from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App
from pianosdk.publisher.models.user import User


class MailLog(BaseModel):
    email_id: Optional[str] = None
    app: Optional['App'] = None
    user: Optional['User'] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    reply_to: Optional[str] = None
    create_date: Optional[str] = None
    open_date: Optional[str] = None
    status: Optional[str] = None
    status_localized: Optional[str] = None
    reject_reason: Optional[str] = None
    email_name: Optional[str] = None
    subject: Optional[str] = None
    body: Optional[str] = None


MailLog.model_rebuild()
