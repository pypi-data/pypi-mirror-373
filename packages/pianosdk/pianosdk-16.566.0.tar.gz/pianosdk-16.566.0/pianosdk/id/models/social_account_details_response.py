from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.social_account_detail import SocialAccountDetail
from typing import List


class SocialAccountDetailsResponse(BaseModel):
    social_accounts: Optional['List[SocialAccountDetail]'] = None


SocialAccountDetailsResponse.model_rebuild()
