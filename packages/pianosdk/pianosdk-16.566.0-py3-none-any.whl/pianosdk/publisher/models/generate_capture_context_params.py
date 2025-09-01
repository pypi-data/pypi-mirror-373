from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class GenerateCaptureContextParams(BaseModel):
    aid: Optional[str] = None
    target_origins: Optional[List[str]] = None
    source_id: Optional[int] = None


GenerateCaptureContextParams.model_rebuild()
