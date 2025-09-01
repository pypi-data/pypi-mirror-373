from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class UserNote(BaseModel):
    user_note_id: Optional[str] = None
    user: Optional['User'] = None
    content: Optional[str] = None
    type: Optional[str] = None
    create_date: Optional[str] = None
    create_by: Optional['User'] = None
    update_date: Optional[str] = None
    update_by: Optional['User'] = None
    readonly: Optional[bool] = None


UserNote.model_rebuild()
