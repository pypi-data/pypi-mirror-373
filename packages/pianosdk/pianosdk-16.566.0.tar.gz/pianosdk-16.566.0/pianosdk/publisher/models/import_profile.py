from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ImportProfile(BaseModel):
    import_profile_id: Optional[str] = None
    name: Optional[str] = None
    source_environment: Optional[str] = None
    source_aid: Optional[str] = None
    source_url: Optional[str] = None
    source_api_token: Optional[str] = None


ImportProfile.model_rebuild()
