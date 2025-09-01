from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.licensee_manager import LicenseeManager
from pianosdk.publisher.models.licensee_representative import LicenseeRepresentative
from typing import List


class Licensee(BaseModel):
    aid: Optional[str] = None
    licensee_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    representatives: Optional['List[LicenseeRepresentative]'] = None
    managers: Optional['List[LicenseeManager]'] = None


Licensee.model_rebuild()
