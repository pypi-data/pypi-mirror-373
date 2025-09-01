from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AfcConfiguration(BaseModel):
    afc_client_id: Optional[str] = None
    afc_username: Optional[str] = None
    afc_password: Optional[str] = None
    afc_client_profile_id: Optional[str] = None


AfcConfiguration.model_rebuild()
