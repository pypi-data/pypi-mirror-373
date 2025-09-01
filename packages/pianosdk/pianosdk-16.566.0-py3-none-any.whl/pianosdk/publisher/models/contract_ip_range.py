from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ContractIpRange(BaseModel):
    ip_range: Optional[str] = None
    contract_ip_range_id: Optional[str] = None
    status: Optional[str] = None


ContractIpRange.model_rebuild()
