from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.address_config import AddressConfig
from typing import List


class ExperianConfiguration(BaseModel):
    experian_token: Optional[str] = None
    pd_address_settings_enabled: Optional[bool] = None
    experian_address_config: Optional['List[AddressConfig]'] = None


ExperianConfiguration.model_rebuild()
