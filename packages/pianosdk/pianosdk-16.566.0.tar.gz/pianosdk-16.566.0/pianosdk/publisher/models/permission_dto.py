from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class PermissionDTO(BaseModel):
    title: Optional[str] = None
    descr: Optional[str] = None
    mnemonic: Optional[str] = None
    defaults: Optional[List[str]] = None


PermissionDTO.model_rebuild()
