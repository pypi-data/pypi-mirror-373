from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseContractUser(BaseModel):
    contract_id: Optional[str] = None
    email: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None


EraseContractUser.model_rebuild()
