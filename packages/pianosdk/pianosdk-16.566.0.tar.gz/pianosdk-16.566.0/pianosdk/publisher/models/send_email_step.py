from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.mail import Mail


class SendEmailStep(BaseModel):
    optional: Optional[bool] = None
    enabled: Optional[bool] = None
    email: Optional['Mail'] = None


SendEmailStep.model_rebuild()
