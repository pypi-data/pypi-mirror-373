from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Composer(BaseModel):
    enabled: Optional[bool] = None


Composer.model_rebuild()
