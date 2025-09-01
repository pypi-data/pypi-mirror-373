from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.error_code import ErrorCode
from pianosdk.publisher.models.error_codes import ErrorCodes
from typing import Any
from typing import List


class Result(BaseModel):
    errors: Optional['List[ErrorCode]'] = None
    error: Optional['ErrorCode'] = None
    error_codes: Optional['ErrorCodes'] = None
    ok: Optional[bool] = None
    or_fail: Optional['Any'] = None
    error_as_string: Optional[str] = None


Result.model_rebuild()
