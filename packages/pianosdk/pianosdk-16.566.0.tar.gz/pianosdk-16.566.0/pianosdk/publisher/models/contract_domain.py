from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ContractDomain(BaseModel):
    contract_domain_value: Optional[str] = None
    contract_domain_id: Optional[str] = None
    status: Optional[str] = None
    contract_users_count: Optional[int] = None
    active_contract_users_count: Optional[int] = None


ContractDomain.model_rebuild()
