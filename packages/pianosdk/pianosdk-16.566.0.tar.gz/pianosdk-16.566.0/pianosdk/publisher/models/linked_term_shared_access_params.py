from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class LinkedTermSharedAccessParams(BaseModel):
    subscription_id: Optional[str] = None
    user_tokens: Optional[List[str]] = None


LinkedTermSharedAccessParams.model_rebuild()
