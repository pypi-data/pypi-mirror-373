from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CommentAction(BaseModel):
    id: Optional[str] = None
    caption: Optional[str] = None


CommentAction.model_rebuild()
