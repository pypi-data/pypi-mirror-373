from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.create_access_period_params import CreateAccessPeriodParams
from typing import List


class CreateBillingConfigurationRequest(BaseModel):
    periods: Optional['List[CreateAccessPeriodParams]'] = None


CreateBillingConfigurationRequest.model_rebuild()
