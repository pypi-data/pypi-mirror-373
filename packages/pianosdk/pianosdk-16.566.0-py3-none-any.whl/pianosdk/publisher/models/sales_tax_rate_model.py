from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SalesTaxRateModel(BaseModel):
    charged: Optional[bool] = None
    charge_rate: Optional[float] = None
    state_abbr: Optional[str] = None
    state_id: Optional[str] = None
    state_name: Optional[str] = None


SalesTaxRateModel.model_rebuild()
