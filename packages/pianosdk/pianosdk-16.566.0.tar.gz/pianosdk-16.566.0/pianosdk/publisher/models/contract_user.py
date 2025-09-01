from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ContractUser(BaseModel):
    email: Optional[str] = None
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    contract_user_id: Optional[str] = None
    status: Optional[str] = None


ContractUser.model_rebuild()
