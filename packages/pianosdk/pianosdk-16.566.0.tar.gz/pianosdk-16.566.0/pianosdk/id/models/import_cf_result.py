from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import Dict
from typing import List


class ImportCFResult(BaseModel):
    code: Optional[int] = None
    ts: Optional[int] = None
    data: Optional['Dict[str, List[Dict[str, str]]]'] = None


ImportCFResult.model_rebuild()
