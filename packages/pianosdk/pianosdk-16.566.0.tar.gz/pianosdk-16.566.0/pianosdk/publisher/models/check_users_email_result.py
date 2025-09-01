from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.import_user import ImportUser
from typing import List


class CheckUsersEmailResult(BaseModel):
    existing_emails: Optional['List[ImportUser]'] = None
    existing_but_not_bounded_emails: Optional['List[ImportUser]'] = None
    new_emails: Optional['List[ImportUser]'] = None
    invalid_emails: Optional['List[ImportUser]'] = None


CheckUsersEmailResult.model_rebuild()
