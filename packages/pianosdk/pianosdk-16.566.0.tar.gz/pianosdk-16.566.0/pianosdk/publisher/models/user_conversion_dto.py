from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.user import User


class UserConversionDTO(BaseModel):
    user: Optional['User'] = None
    term: Optional['Term'] = None


UserConversionDTO.model_rebuild()
