from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.update_access_period_params import UpdateAccessPeriodParams
from typing import List


class UpdateBillingConfigurationRequest(BaseModel):
    periods: Optional['List[UpdateAccessPeriodParams]'] = None


UpdateBillingConfigurationRequest.model_rebuild()
