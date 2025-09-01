from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class RenderedEmail(BaseModel):
    body: Optional[str] = None
    subject: Optional[str] = None


RenderedEmail.model_rebuild()
