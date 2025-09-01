from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class InquiryComment(BaseModel):
    comment_id: Optional[str] = None
    submitter_type: Optional[int] = None
    create_date: Optional[str] = None
    message: Optional[str] = None
    user: Optional['User'] = None
    email: Optional[str] = None
    name: Optional[str] = None
    personal_name: Optional[str] = None
    internal: Optional[str] = None


InquiryComment.model_rebuild()
