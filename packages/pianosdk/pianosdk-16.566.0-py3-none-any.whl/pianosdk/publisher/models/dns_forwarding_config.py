from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DnsForwardingConfig(BaseModel):
    aid: Optional[str] = None
    config_id: Optional[str] = None
    status: Optional[str] = None
    cname_status: Optional[str] = None
    ssl_status: Optional[str] = None
    content: Optional[str] = None


DnsForwardingConfig.model_rebuild()
