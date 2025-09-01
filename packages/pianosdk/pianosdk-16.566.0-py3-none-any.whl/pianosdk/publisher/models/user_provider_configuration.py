from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App
from typing import Any
from typing import Dict
from typing import List


class UserProviderConfiguration(BaseModel):
    user_provider_configuration_id: Optional[str] = None
    app: Optional['App'] = None
    source: Optional[str] = None
    title: Optional[str] = None
    app_id: Optional[str] = None
    app_name: Optional[str] = None
    client_secret: Optional[str] = None
    client_id: Optional[str] = None
    type_name: Optional[str] = None
    reset_password_client_id: Optional[str] = None
    reset_password_flow: Optional[str] = None
    reset_password_flow_version: Optional[str] = None
    reset_password_locale: Optional[str] = None
    reset_password_redirect_uri: Optional[str] = None
    reset_password_form: Optional[str] = None
    api_version: Optional[str] = None
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    auth_key: Optional[str] = None
    site_code: Optional[str] = None
    reset_password_template_name: Optional[str] = None
    reset_password_sender: Optional[str] = None
    reset_password_logo_url: Optional[str] = None
    reset_password_brand_name: Optional[str] = None
    reset_password_login_url: Optional[str] = None
    reset_password_site_base_url: Optional[str] = None
    reset_password_privacy_policy_url: Optional[str] = None
    reset_password_user_agreement_url: Optional[str] = None
    is_disabled: Optional[bool] = None
    is_editable: Optional[bool] = None
    secret_key: Optional[str] = None
    user_key: Optional[str] = None
    gigya_datacenter_url: Optional[str] = None
    gigya_passwordless_captcha_enabled: Optional[bool] = None
    gigya_passwordless_login_on_gift_redemption_enabled: Optional[bool] = None
    shared_secret: Optional[str] = None
    reset_password_landing_page_url: Optional[str] = None
    passwordless_magic_link_url: Optional[str] = None
    oauth_client_secret: Optional[str] = None
    token_expiration_time: Optional[int] = None
    password_reset_link_expiration_time_in_hours: Optional[int] = None
    deployment_host: Optional[str] = None
    password_minimal_length: Optional[int] = None
    password_has_mixed_case: Optional[bool] = None
    password_has_alphanumeric: Optional[bool] = None
    password_has_special_characters: Optional[bool] = None
    password_has_no_email: Optional[bool] = None
    use_captcha: Optional[bool] = None
    captcha_version: Optional[str] = None
    captcha_screen: Optional[str] = None
    captcha3_site_key: Optional[str] = None
    captcha3_secret_key: Optional[str] = None
    reset_password_captcha: Optional[bool] = None
    authentication_attempts_to_show_captcha: Optional[int] = None
    piano_id_captcha_settings: Optional[str] = None
    message_login_failed: Optional[str] = None
    social_callback_url: Optional[str] = None
    social_settings: Optional[str] = None
    piano_id_main_settings: Optional[str] = None
    require_first_and_last_names: Optional[bool] = None
    override_shared_secret_for_global_mode: Optional[bool] = None
    disable_custom_fields_user_mining: Optional[bool] = None
    disable_custom_fields_counters: Optional[bool] = None
    client_custom_fields_validation: Optional[bool] = None
    extend_expired_access_enabled: Optional[bool] = None
    passwordless_login_enabled: Optional[bool] = None
    redirect_uri_whitelist: Optional[List[str]] = None
    redirect_uri_whitelist_confirmed: Optional[bool] = None
    external_identity_providers: Optional[str] = None
    custom_fields: Optional['List[Dict[str, Any]]'] = None
    overridden_settings: Optional[str] = None


UserProviderConfiguration.model_rebuild()
