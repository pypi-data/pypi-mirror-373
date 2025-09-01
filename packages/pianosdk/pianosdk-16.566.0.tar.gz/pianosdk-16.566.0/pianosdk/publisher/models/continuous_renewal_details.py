from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ContinuousRenewalDetails(BaseModel):
    enabled: Optional[bool] = None


ContinuousRenewalDetails.model_rebuild()
