from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.social_linking_response import SocialLinkingResponse


class TokenResponse(BaseModel):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    refresh_token: Optional[str] = None
    code: Optional[str] = None
    error: Optional[str] = None
    error_description: Optional[str] = None
    expires_in: Optional[int] = None
    preauth_token: Optional[str] = None
    social_linking_response: Optional['SocialLinkingResponse'] = None
    registration: Optional[bool] = None
    site_cookie_domain: Optional[str] = None
    email_confirmation_required: Optional[bool] = None
    pre_confirmed_user: Optional[bool] = None
    login_token_id: Optional[str] = None
    extend_expired_access_enabled: Optional[bool] = None
    direction_url: Optional[str] = None
    passwordless_token: Optional[str] = None
    pub_id: Optional[str] = None
    authorized_by_sso: Optional[bool] = None
    message: Optional[str] = None
    sso_confirmation: Optional[bool] = None
    two_factor_auth_required: Optional[bool] = None
    phone_confirmation_required: Optional[bool] = None


TokenResponse.model_rebuild()
