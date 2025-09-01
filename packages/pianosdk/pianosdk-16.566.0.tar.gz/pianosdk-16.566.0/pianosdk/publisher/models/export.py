from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Export(BaseModel):
    export_id: Optional[str] = None
    export_name: Optional[str] = None
    export_created: Optional[datetime] = None
    export_completed: Optional[datetime] = None
    export_percentage: Optional[int] = None
    export_records: Optional[int] = None
    export_status: Optional[str] = None
    report_type: Optional[str] = None
    export_updated: Optional[datetime] = None
    export_repeatable: Optional[bool] = None
    filter_data: Optional[str] = None


Export.model_rebuild()
