from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EigenCreateCreditCardInfoDto(BaseModel):
    integration_version: Optional[str] = None


EigenCreateCreditCardInfoDto.model_rebuild()
