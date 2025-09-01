from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BrainTreeCreateCreditCardInfoDto(BaseModel):
    braintree_client_token: Optional[str] = None
    version: Optional[str] = None
    braintree_client_key: Optional[str] = None
    authorization_amount: Optional[float] = None
    collect_cardholder_name: Optional[bool] = None


BrainTreeCreateCreditCardInfoDto.model_rebuild()
