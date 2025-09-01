from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class MailOptionsVerificationResult(BaseModel):
    dkim: Optional[bool] = None
    dkim_tokens: Optional[List[str]] = None
    spf: Optional[bool] = None
    spf_record: Optional[str] = None
    txt: Optional[bool] = None
    txt_token: Optional[str] = None
    email_verify_status: Optional[str] = None
    verified_email: Optional[str] = None
    email_provider: Optional[str] = None
    email_domain_verified: Optional[bool] = None


MailOptionsVerificationResult.model_rebuild()
