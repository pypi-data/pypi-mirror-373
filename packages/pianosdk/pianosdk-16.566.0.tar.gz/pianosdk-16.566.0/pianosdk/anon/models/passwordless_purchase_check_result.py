from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.resource import Resource


class PasswordlessPurchaseCheckResult(BaseModel):
    poll_status: Optional[str] = None
    resource: Optional['Resource'] = None
    show_offer_params: Optional[str] = None
    type: Optional[str] = None


PasswordlessPurchaseCheckResult.model_rebuild()
