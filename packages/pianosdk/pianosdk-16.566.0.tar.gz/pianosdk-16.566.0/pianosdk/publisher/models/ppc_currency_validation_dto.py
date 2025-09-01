from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class PpcCurrencyValidationDto(BaseModel):
    number_of_subscription: Optional[int] = None
    list_of_currencies: Optional[List[str]] = None
    can_be_deleted: Optional[bool] = None
    has_error: Optional[bool] = None


PpcCurrencyValidationDto.model_rebuild()
