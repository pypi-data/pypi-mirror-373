from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.resource import Resource
from typing import List


class PasswordlessPurchaseCompleteResult(BaseModel):
    oid: Optional[str] = None
    url: Optional[str] = None
    resource: Optional['Resource'] = None
    show_offer_params: Optional[str] = None
    type: Optional[str] = None
    process_id: Optional[str] = None
    polling_enabled: Optional[bool] = None
    polling_timeouts: Optional[List[int]] = None


PasswordlessPurchaseCompleteResult.model_rebuild()
