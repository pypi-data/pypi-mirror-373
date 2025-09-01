from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import Any
from typing import Dict
from typing import List


class Validator(BaseModel):
    type: Optional[str] = None
    params: Optional['Dict[str, Any]'] = None
    error_message: Optional[str] = None


Validator.model_rebuild()
