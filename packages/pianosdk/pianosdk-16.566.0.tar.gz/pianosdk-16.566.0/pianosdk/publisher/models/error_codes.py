from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.error_code import ErrorCode
from typing import List


class ErrorCodes(BaseModel):
    errors: Optional['List[ErrorCode]'] = None
    error: Optional['ErrorCode'] = None


ErrorCodes.model_rebuild()
