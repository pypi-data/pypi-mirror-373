from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BulkUserImportProcessingRequestDto(BaseModel):
    bulk_user_import_id: Optional[str] = None
    bulk_user_import_created: Optional[datetime] = None
    bulk_user_import_total_user_count: Optional[int] = None
    bulk_user_import_processed_user_count: Optional[int] = None


BulkUserImportProcessingRequestDto.model_rebuild()
