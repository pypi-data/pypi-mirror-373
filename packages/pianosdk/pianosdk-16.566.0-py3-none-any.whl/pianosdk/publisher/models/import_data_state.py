from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ImportDataState(BaseModel):
    import_data_id: Optional[str] = None
    import_data_status: Optional[str] = None


ImportDataState.model_rebuild()
