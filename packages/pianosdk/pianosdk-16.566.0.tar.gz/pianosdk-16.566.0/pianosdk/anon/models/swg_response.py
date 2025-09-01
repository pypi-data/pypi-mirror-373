from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class SwgResponse(BaseModel):
    subscription_token: Optional[str] = None
    detail: Optional[str] = None
    products: Optional[List[str]] = None


SwgResponse.model_rebuild()
