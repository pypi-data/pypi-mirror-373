from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.currency import Currency
from typing import List


class DatatransProperties(BaseModel):
    currencies: Optional['List[Currency]'] = None
    collect_cardholder_name: Optional[bool] = None


DatatransProperties.model_rebuild()
