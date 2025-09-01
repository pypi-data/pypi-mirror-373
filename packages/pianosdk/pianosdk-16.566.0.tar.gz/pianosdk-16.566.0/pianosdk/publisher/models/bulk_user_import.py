from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BulkUserImport(BaseModel):
    bulk_user_import_id: Optional[str] = None
    bulk_user_import_created: Optional[datetime] = None
    bulk_user_import_completed: Optional[datetime] = None


BulkUserImport.model_rebuild()
