from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CheckCanUpgradeResult(BaseModel):
    email: Optional[str] = None
    error_message: Optional[str] = None
    error_code: Optional[int] = None
    is_success: Optional[bool] = None


CheckCanUpgradeResult.model_rebuild()
