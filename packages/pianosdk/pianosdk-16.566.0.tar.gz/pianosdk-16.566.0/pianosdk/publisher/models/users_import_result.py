from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.import_user import ImportUser
from typing import List


class UsersImportResult(BaseModel):
    failed_to_process_emails: Optional['List[ImportUser]'] = None


UsersImportResult.model_rebuild()
