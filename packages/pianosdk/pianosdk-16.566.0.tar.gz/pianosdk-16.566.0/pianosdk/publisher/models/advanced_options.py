from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class AdvancedOptions(BaseModel):
    show_options: Optional[List[str]] = None


AdvancedOptions.model_rebuild()
