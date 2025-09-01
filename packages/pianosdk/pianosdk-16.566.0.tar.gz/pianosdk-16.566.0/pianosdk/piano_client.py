from pianosdk.user.api.user_api import UserApi
from pianosdk.user.api.user_access_api import UserAccessApi
from pianosdk.publisher.api.publisher_adblocker_api import PublisherAdblockerApi
from pianosdk.publisher.api.publisher_afc_configuration_api import PublisherAfcConfigurationApi
from pianosdk.publisher.api.publisher_app_api import PublisherAppApi
from pianosdk.publisher.api.publisher_app_api_token_api import PublisherAppApiTokenApi
from pianosdk.publisher.api.publisher_app_features_api import PublisherAppFeaturesApi
from pianosdk.publisher.api.publisher_consent_api import PublisherConsentApi
from pianosdk.publisher.api.publisher_consent_entry_api import PublisherConsentEntryApi
from pianosdk.publisher.api.publisher_conversion_api import PublisherConversionApi
from pianosdk.publisher.api.publisher_conversion_custom_api import PublisherConversionCustomApi
from pianosdk.publisher.api.publisher_conversion_data_api import PublisherConversionDataApi
from pianosdk.publisher.api.publisher_conversion_external_api import PublisherConversionExternalApi
from pianosdk.publisher.api.publisher_conversion_registration_api import PublisherConversionRegistrationApi
from pianosdk.publisher.api.publisher_email_confirmation_api import PublisherEmailConfirmationApi
from pianosdk.publisher.api.publisher_experience_metadata_api import PublisherExperienceMetadataApi
from pianosdk.publisher.api.publisher_export_api import PublisherExportApi
from pianosdk.publisher.api.publisher_export_create_api import PublisherExportCreateApi
from pianosdk.publisher.api.publisher_export_create_aam_api import PublisherExportCreateAamApi
from pianosdk.publisher.api.publisher_export_create_aam_monthly_api import PublisherExportCreateAamMonthlyApi
from pianosdk.publisher.api.publisher_export_create_access_report_export_api import PublisherExportCreateAccessReportExportApi
from pianosdk.publisher.api.publisher_export_create_subscription_details_report_api import PublisherExportCreateSubscriptionDetailsReportApi
from pianosdk.publisher.api.publisher_export_create_transactions_report_api import PublisherExportCreateTransactionsReportApi
from pianosdk.publisher.api.publisher_external_provider_payment_api import PublisherExternalProviderPaymentApi
from pianosdk.publisher.api.publisher_gdpr_api import PublisherGdprApi
from pianosdk.publisher.api.publisher_inquiry_api import PublisherInquiryApi
from pianosdk.publisher.api.publisher_licensing_contract_api import PublisherLicensingContractApi
from pianosdk.publisher.api.publisher_licensing_contract_domain_api import PublisherLicensingContractDomainApi
from pianosdk.publisher.api.publisher_licensing_contract_domain_contract_user_api import PublisherLicensingContractDomainContractUserApi
from pianosdk.publisher.api.publisher_licensing_contract_ip_range_api import PublisherLicensingContractIpRangeApi
from pianosdk.publisher.api.publisher_licensing_contract_periods_api import PublisherLicensingContractPeriodsApi
from pianosdk.publisher.api.publisher_licensing_contract_user_api import PublisherLicensingContractUserApi
from pianosdk.publisher.api.publisher_licensing_licensee_api import PublisherLicensingLicenseeApi
from pianosdk.publisher.api.publisher_licensing_notification_api import PublisherLicensingNotificationApi
from pianosdk.publisher.api.publisher_licensing_notification_rule_api import PublisherLicensingNotificationRuleApi
from pianosdk.publisher.api.publisher_licensing_schedule_api import PublisherLicensingScheduleApi
from pianosdk.publisher.api.publisher_licensing_schedule_contract_periods_api import PublisherLicensingScheduleContractPeriodsApi
from pianosdk.publisher.api.publisher_linked_term_api import PublisherLinkedTermApi
from pianosdk.publisher.api.publisher_linked_term_custom_field_api import PublisherLinkedTermCustomFieldApi
from pianosdk.publisher.api.publisher_offer_api import PublisherOfferApi
from pianosdk.publisher.api.publisher_offer_template_api import PublisherOfferTemplateApi
from pianosdk.publisher.api.publisher_offer_template_create_api import PublisherOfferTemplateCreateApi
from pianosdk.publisher.api.publisher_offer_template_inherited_api import PublisherOfferTemplateInheritedApi
from pianosdk.publisher.api.publisher_offer_template_update_api import PublisherOfferTemplateUpdateApi
from pianosdk.publisher.api.publisher_offer_template_variant_api import PublisherOfferTemplateVariantApi
from pianosdk.publisher.api.publisher_offer_term_api import PublisherOfferTermApi
from pianosdk.publisher.api.publisher_offer_term_offer_api import PublisherOfferTermOfferApi
from pianosdk.publisher.api.publisher_payment_api import PublisherPaymentApi
from pianosdk.publisher.api.publisher_payment_method_api import PublisherPaymentMethodApi
from pianosdk.publisher.api.publisher_payment_method_billing_address_api import PublisherPaymentMethodBillingAddressApi
from pianosdk.publisher.api.publisher_payment_method_gmo_api import PublisherPaymentMethodGmoApi
from pianosdk.publisher.api.publisher_payment_provider_configuration_api import PublisherPaymentProviderConfigurationApi
from pianosdk.publisher.api.publisher_promotion_api import PublisherPromotionApi
from pianosdk.publisher.api.publisher_promotion_code_api import PublisherPromotionCodeApi
from pianosdk.publisher.api.publisher_promotion_fixed_discount_api import PublisherPromotionFixedDiscountApi
from pianosdk.publisher.api.publisher_promotion_term_api import PublisherPromotionTermApi
from pianosdk.publisher.api.publisher_resource_api import PublisherResourceApi
from pianosdk.publisher.api.publisher_resource_bundle_api import PublisherResourceBundleApi
from pianosdk.publisher.api.publisher_resource_cross_app_api import PublisherResourceCrossAppApi
from pianosdk.publisher.api.publisher_resource_stats_api import PublisherResourceStatsApi
from pianosdk.publisher.api.publisher_resource_tag_api import PublisherResourceTagApi
from pianosdk.publisher.api.publisher_resource_user_api import PublisherResourceUserApi
from pianosdk.publisher.api.publisher_schedule_api import PublisherScheduleApi
from pianosdk.publisher.api.publisher_schedule_period_api import PublisherSchedulePeriodApi
from pianosdk.publisher.api.publisher_subscription_api import PublisherSubscriptionApi
from pianosdk.publisher.api.publisher_subscription_address_api import PublisherSubscriptionAddressApi
from pianosdk.publisher.api.publisher_subscription_cancel_api import PublisherSubscriptionCancelApi
from pianosdk.publisher.api.publisher_subscription_share_api import PublisherSubscriptionShareApi
from pianosdk.publisher.api.publisher_subscription_share_user_api import PublisherSubscriptionShareUserApi
from pianosdk.publisher.api.publisher_team_api import PublisherTeamApi
from pianosdk.publisher.api.publisher_term_api import PublisherTermApi
from pianosdk.publisher.api.publisher_term_change_api import PublisherTermChangeApi
from pianosdk.publisher.api.publisher_term_change_option_api import PublisherTermChangeOptionApi
from pianosdk.publisher.api.publisher_term_custom_api import PublisherTermCustomApi
from pianosdk.publisher.api.publisher_term_dynamic_api import PublisherTermDynamicApi
from pianosdk.publisher.api.publisher_term_external_api import PublisherTermExternalApi
from pianosdk.publisher.api.publisher_term_gift_api import PublisherTermGiftApi
from pianosdk.publisher.api.publisher_term_payment_api import PublisherTermPaymentApi
from pianosdk.publisher.api.publisher_term_registration_api import PublisherTermRegistrationApi
from pianosdk.publisher.api.publisher_term_stats_api import PublisherTermStatsApi
from pianosdk.publisher.api.publisher_test_api import PublisherTestApi
from pianosdk.publisher.api.publisher_user_api import PublisherUserApi
from pianosdk.publisher.api.publisher_user_access_api import PublisherUserAccessApi
from pianosdk.publisher.api.publisher_user_access_active_api import PublisherUserAccessActiveApi
from pianosdk.publisher.api.publisher_user_address_api import PublisherUserAddressApi
from pianosdk.publisher.api.publisher_user_app_api import PublisherUserAppApi
from pianosdk.publisher.api.publisher_user_billing_address_api import PublisherUserBillingAddressApi
from pianosdk.publisher.api.publisher_user_bulk_import_api import PublisherUserBulkImportApi
from pianosdk.publisher.api.publisher_user_email_api import PublisherUserEmailApi
from pianosdk.publisher.api.publisher_user_list_api import PublisherUserListApi
from pianosdk.publisher.api.publisher_user_note_api import PublisherUserNoteApi
from pianosdk.publisher.api.publisher_voucher_api import PublisherVoucherApi
from pianosdk.publisher.api.publisher_webhook_api import PublisherWebhookApi
from pianosdk.publisher.api.publisher_webhook_response_api import PublisherWebhookResponseApi
from pianosdk.publisher.api.publisher_webhook_settings_api import PublisherWebhookSettingsApi
from pianosdk.anon.api.access_api import AccessApi
from pianosdk.anon.api.access_token_api import AccessTokenApi
from pianosdk.anon.api.anon_assets_api import AnonAssetsApi
from pianosdk.anon.api.anon_country_list_api import AnonCountryListApi
from pianosdk.anon.api.anon_error_api import AnonErrorApi
from pianosdk.anon.api.anon_mobile_sdk_id_deployment_api import AnonMobileSdkIdDeploymentApi
from pianosdk.anon.api.anon_user_api import AnonUserApi
from pianosdk.anon.api.anon_user_disable_api import AnonUserDisableApi
from pianosdk.anon.api.conversion_api import ConversionApi
from pianosdk.anon.api.conversion_external_api import ConversionExternalApi
from pianosdk.anon.api.conversion_registration_api import ConversionRegistrationApi
from pianosdk.anon.api.email_confirmation_api import EmailConfirmationApi
from pianosdk.anon.api.exposure_api import ExposureApi
from pianosdk.anon.api.oauth_api import OauthApi
from pianosdk.anon.api.subscription_api import SubscriptionApi
from pianosdk.anon.api.swg_sync_api import SwgSyncApi
from pianosdk.id.api.identity_api import IdentityApi
from pianosdk.id.api.identity_oauth_api import IdentityOauthApi
from pianosdk.id.api.identity_token_api import IdentityTokenApi
from pianosdk.id.api.publisher_api import PublisherApi
from pianosdk.id.api.publisher_audit_api import PublisherAuditApi
from pianosdk.id.api.publisher_form_api import PublisherFormApi
from pianosdk.id.api.publisher_identity_api import PublisherIdentityApi
from pianosdk.id.api.publisher_identity_doi_api import PublisherIdentityDoiApi
from pianosdk.id.api.publisher_identity_session_api import PublisherIdentitySessionApi
from pianosdk.id.api.publisher_identity_set_api import PublisherIdentitySetApi
from pianosdk.id.api.publisher_import_custom_fields_api import PublisherImportCustomFieldsApi
from pianosdk.id.api.publisher_link_api import PublisherLinkApi
from pianosdk.id.api.publisher_login_api import PublisherLoginApi
from pianosdk.id.api.publisher_login_social_api import PublisherLoginSocialApi
from pianosdk.id.api.publisher_reset_api import PublisherResetApi
from pianosdk.id.api.publisher_social_api import PublisherSocialApi
from pianosdk.id.api.publisher_token_api import PublisherTokenApi
from pianosdk.id.api.publisher_userinfo_api import PublisherUserinfoApi
from pianosdk.id.api.publisher_users_api import PublisherUsersApi
import json
from datetime import datetime, timezone
from typing import Dict

from pianosdk import HttpCallBack
from pianosdk.configuration import Configuration
from pianosdk.utils import cached_property, _encrypt, _decrypt, _encode_parameter
from pianosdk.webhook_events import _event_types_mapping, Event


class Client:
    def __init__(self, timeout: int = 60, max_retries: int = 3, backoff_factor: int = 0,
                 api_host: str = 'production', api_token: str = 'TODO: Replace', private_key: str = 'TODO: Replace',
                 additional_headers: Dict = None, config: Configuration = None, http_callback: HttpCallBack = None) -> None:
        """
        API client. It will use provided `config` or will build configuration from other parameters
        :param timeout: The value to use for connection timeout
        :param max_retries: The number of times to retry failed endpoint call
        :param backoff_factor: A backoff factor to apply between attempts after the second try.
        :param api_host: API host. Use `production`, `sandbox` or custom url
        :param api_token: Api Token
        :param private_key: Private key
        :param additional_headers: Additional headers to add to each API request
        :param config: Prebuilt configuration
        :param http_callback: Http method call back to intercept raw requests or responses
        """
        if config is None:
            self.config = Configuration(timeout=timeout,
                                        max_retries=max_retries,
                                        backoff_factor=backoff_factor,
                                        api_host=api_host,
                                        api_token=api_token,
                                        private_key=private_key,
                                        additional_headers=additional_headers)
        else:
            self.config = config
        self.http_callback = http_callback

    def userref_create(self, uid: str, email: str, first_name: str = None, last_name: str = None,
                       create_date: datetime = None) -> str:
        """
        Build User reference
        :param uid: User id
        :param email: User's email
        :param first_name: User's first name
        :param last_name: User's last name
        :param create_date: User's create date
        :return: Encrypted user reference for Piano backend
        """
        data = {
            'uid': uid,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'create_date': create_date and str(_encode_parameter(create_date)),
            'timestamp': str(_encode_parameter(datetime.utcnow()))
        }
        data = {k: v for k, v in data.items() if v is not None}
        return _encrypt(self.config.private_key, json.dumps(data))

    def parse_webhook_data(self, value: str) -> Event:
        """
        Parse webhook event
        :param value: Encrypted webhook data
        :return: Event object
        """
        text = _decrypt(self.config.private_key, value)
        data = json.loads(text)
        event_type = data.get('type')
        if not event_type:
            raise ValueError("Event type missed, can't parse it")
        cls = _event_types_mapping.get(event_type)
        if not cls:
            raise ValueError(f'Unknown event type {event_type}')
        return cls(**data)

    @cached_property
    def user_api(self) -> UserApi:
        return UserApi(self.config, self.http_callback)

    @cached_property
    def user_access_api(self) -> UserAccessApi:
        return UserAccessApi(self.config, self.http_callback)

    @cached_property
    def publisher_adblocker_api(self) -> PublisherAdblockerApi:
        return PublisherAdblockerApi(self.config, self.http_callback)

    @cached_property
    def publisher_afc_configuration_api(self) -> PublisherAfcConfigurationApi:
        return PublisherAfcConfigurationApi(self.config, self.http_callback)

    @cached_property
    def publisher_app_api(self) -> PublisherAppApi:
        return PublisherAppApi(self.config, self.http_callback)

    @cached_property
    def publisher_app_api_token_api(self) -> PublisherAppApiTokenApi:
        return PublisherAppApiTokenApi(self.config, self.http_callback)

    @cached_property
    def publisher_app_features_api(self) -> PublisherAppFeaturesApi:
        return PublisherAppFeaturesApi(self.config, self.http_callback)

    @cached_property
    def publisher_consent_api(self) -> PublisherConsentApi:
        return PublisherConsentApi(self.config, self.http_callback)

    @cached_property
    def publisher_consent_entry_api(self) -> PublisherConsentEntryApi:
        return PublisherConsentEntryApi(self.config, self.http_callback)

    @cached_property
    def publisher_conversion_api(self) -> PublisherConversionApi:
        return PublisherConversionApi(self.config, self.http_callback)

    @cached_property
    def publisher_conversion_custom_api(self) -> PublisherConversionCustomApi:
        return PublisherConversionCustomApi(self.config, self.http_callback)

    @cached_property
    def publisher_conversion_data_api(self) -> PublisherConversionDataApi:
        return PublisherConversionDataApi(self.config, self.http_callback)

    @cached_property
    def publisher_conversion_external_api(self) -> PublisherConversionExternalApi:
        return PublisherConversionExternalApi(self.config, self.http_callback)

    @cached_property
    def publisher_conversion_registration_api(self) -> PublisherConversionRegistrationApi:
        return PublisherConversionRegistrationApi(self.config, self.http_callback)

    @cached_property
    def publisher_email_confirmation_api(self) -> PublisherEmailConfirmationApi:
        return PublisherEmailConfirmationApi(self.config, self.http_callback)

    @cached_property
    def publisher_experience_metadata_api(self) -> PublisherExperienceMetadataApi:
        return PublisherExperienceMetadataApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_api(self) -> PublisherExportApi:
        return PublisherExportApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_create_api(self) -> PublisherExportCreateApi:
        return PublisherExportCreateApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_create_aam_api(self) -> PublisherExportCreateAamApi:
        return PublisherExportCreateAamApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_create_aam_monthly_api(self) -> PublisherExportCreateAamMonthlyApi:
        return PublisherExportCreateAamMonthlyApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_create_access_report_export_api(self) -> PublisherExportCreateAccessReportExportApi:
        return PublisherExportCreateAccessReportExportApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_create_subscription_details_report_api(self) -> PublisherExportCreateSubscriptionDetailsReportApi:
        return PublisherExportCreateSubscriptionDetailsReportApi(self.config, self.http_callback)

    @cached_property
    def publisher_export_create_transactions_report_api(self) -> PublisherExportCreateTransactionsReportApi:
        return PublisherExportCreateTransactionsReportApi(self.config, self.http_callback)

    @cached_property
    def publisher_external_provider_payment_api(self) -> PublisherExternalProviderPaymentApi:
        return PublisherExternalProviderPaymentApi(self.config, self.http_callback)

    @cached_property
    def publisher_gdpr_api(self) -> PublisherGdprApi:
        return PublisherGdprApi(self.config, self.http_callback)

    @cached_property
    def publisher_inquiry_api(self) -> PublisherInquiryApi:
        return PublisherInquiryApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_contract_api(self) -> PublisherLicensingContractApi:
        return PublisherLicensingContractApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_contract_domain_api(self) -> PublisherLicensingContractDomainApi:
        return PublisherLicensingContractDomainApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_contract_domain_contract_user_api(self) -> PublisherLicensingContractDomainContractUserApi:
        return PublisherLicensingContractDomainContractUserApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_contract_ip_range_api(self) -> PublisherLicensingContractIpRangeApi:
        return PublisherLicensingContractIpRangeApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_contract_periods_api(self) -> PublisherLicensingContractPeriodsApi:
        return PublisherLicensingContractPeriodsApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_contract_user_api(self) -> PublisherLicensingContractUserApi:
        return PublisherLicensingContractUserApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_licensee_api(self) -> PublisherLicensingLicenseeApi:
        return PublisherLicensingLicenseeApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_notification_api(self) -> PublisherLicensingNotificationApi:
        return PublisherLicensingNotificationApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_notification_rule_api(self) -> PublisherLicensingNotificationRuleApi:
        return PublisherLicensingNotificationRuleApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_schedule_api(self) -> PublisherLicensingScheduleApi:
        return PublisherLicensingScheduleApi(self.config, self.http_callback)

    @cached_property
    def publisher_licensing_schedule_contract_periods_api(self) -> PublisherLicensingScheduleContractPeriodsApi:
        return PublisherLicensingScheduleContractPeriodsApi(self.config, self.http_callback)

    @cached_property
    def publisher_linked_term_api(self) -> PublisherLinkedTermApi:
        return PublisherLinkedTermApi(self.config, self.http_callback)

    @cached_property
    def publisher_linked_term_custom_field_api(self) -> PublisherLinkedTermCustomFieldApi:
        return PublisherLinkedTermCustomFieldApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_api(self) -> PublisherOfferApi:
        return PublisherOfferApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_template_api(self) -> PublisherOfferTemplateApi:
        return PublisherOfferTemplateApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_template_create_api(self) -> PublisherOfferTemplateCreateApi:
        return PublisherOfferTemplateCreateApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_template_inherited_api(self) -> PublisherOfferTemplateInheritedApi:
        return PublisherOfferTemplateInheritedApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_template_update_api(self) -> PublisherOfferTemplateUpdateApi:
        return PublisherOfferTemplateUpdateApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_template_variant_api(self) -> PublisherOfferTemplateVariantApi:
        return PublisherOfferTemplateVariantApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_term_api(self) -> PublisherOfferTermApi:
        return PublisherOfferTermApi(self.config, self.http_callback)

    @cached_property
    def publisher_offer_term_offer_api(self) -> PublisherOfferTermOfferApi:
        return PublisherOfferTermOfferApi(self.config, self.http_callback)

    @cached_property
    def publisher_payment_api(self) -> PublisherPaymentApi:
        return PublisherPaymentApi(self.config, self.http_callback)

    @cached_property
    def publisher_payment_method_api(self) -> PublisherPaymentMethodApi:
        return PublisherPaymentMethodApi(self.config, self.http_callback)

    @cached_property
    def publisher_payment_method_billing_address_api(self) -> PublisherPaymentMethodBillingAddressApi:
        return PublisherPaymentMethodBillingAddressApi(self.config, self.http_callback)

    @cached_property
    def publisher_payment_method_gmo_api(self) -> PublisherPaymentMethodGmoApi:
        return PublisherPaymentMethodGmoApi(self.config, self.http_callback)

    @cached_property
    def publisher_payment_provider_configuration_api(self) -> PublisherPaymentProviderConfigurationApi:
        return PublisherPaymentProviderConfigurationApi(self.config, self.http_callback)

    @cached_property
    def publisher_promotion_api(self) -> PublisherPromotionApi:
        return PublisherPromotionApi(self.config, self.http_callback)

    @cached_property
    def publisher_promotion_code_api(self) -> PublisherPromotionCodeApi:
        return PublisherPromotionCodeApi(self.config, self.http_callback)

    @cached_property
    def publisher_promotion_fixed_discount_api(self) -> PublisherPromotionFixedDiscountApi:
        return PublisherPromotionFixedDiscountApi(self.config, self.http_callback)

    @cached_property
    def publisher_promotion_term_api(self) -> PublisherPromotionTermApi:
        return PublisherPromotionTermApi(self.config, self.http_callback)

    @cached_property
    def publisher_resource_api(self) -> PublisherResourceApi:
        return PublisherResourceApi(self.config, self.http_callback)

    @cached_property
    def publisher_resource_bundle_api(self) -> PublisherResourceBundleApi:
        return PublisherResourceBundleApi(self.config, self.http_callback)

    @cached_property
    def publisher_resource_cross_app_api(self) -> PublisherResourceCrossAppApi:
        return PublisherResourceCrossAppApi(self.config, self.http_callback)

    @cached_property
    def publisher_resource_stats_api(self) -> PublisherResourceStatsApi:
        return PublisherResourceStatsApi(self.config, self.http_callback)

    @cached_property
    def publisher_resource_tag_api(self) -> PublisherResourceTagApi:
        return PublisherResourceTagApi(self.config, self.http_callback)

    @cached_property
    def publisher_resource_user_api(self) -> PublisherResourceUserApi:
        return PublisherResourceUserApi(self.config, self.http_callback)

    @cached_property
    def publisher_schedule_api(self) -> PublisherScheduleApi:
        return PublisherScheduleApi(self.config, self.http_callback)

    @cached_property
    def publisher_schedule_period_api(self) -> PublisherSchedulePeriodApi:
        return PublisherSchedulePeriodApi(self.config, self.http_callback)

    @cached_property
    def publisher_subscription_api(self) -> PublisherSubscriptionApi:
        return PublisherSubscriptionApi(self.config, self.http_callback)

    @cached_property
    def publisher_subscription_address_api(self) -> PublisherSubscriptionAddressApi:
        return PublisherSubscriptionAddressApi(self.config, self.http_callback)

    @cached_property
    def publisher_subscription_cancel_api(self) -> PublisherSubscriptionCancelApi:
        return PublisherSubscriptionCancelApi(self.config, self.http_callback)

    @cached_property
    def publisher_subscription_share_api(self) -> PublisherSubscriptionShareApi:
        return PublisherSubscriptionShareApi(self.config, self.http_callback)

    @cached_property
    def publisher_subscription_share_user_api(self) -> PublisherSubscriptionShareUserApi:
        return PublisherSubscriptionShareUserApi(self.config, self.http_callback)

    @cached_property
    def publisher_team_api(self) -> PublisherTeamApi:
        return PublisherTeamApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_api(self) -> PublisherTermApi:
        return PublisherTermApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_change_api(self) -> PublisherTermChangeApi:
        return PublisherTermChangeApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_change_option_api(self) -> PublisherTermChangeOptionApi:
        return PublisherTermChangeOptionApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_custom_api(self) -> PublisherTermCustomApi:
        return PublisherTermCustomApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_dynamic_api(self) -> PublisherTermDynamicApi:
        return PublisherTermDynamicApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_external_api(self) -> PublisherTermExternalApi:
        return PublisherTermExternalApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_gift_api(self) -> PublisherTermGiftApi:
        return PublisherTermGiftApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_payment_api(self) -> PublisherTermPaymentApi:
        return PublisherTermPaymentApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_registration_api(self) -> PublisherTermRegistrationApi:
        return PublisherTermRegistrationApi(self.config, self.http_callback)

    @cached_property
    def publisher_term_stats_api(self) -> PublisherTermStatsApi:
        return PublisherTermStatsApi(self.config, self.http_callback)

    @cached_property
    def publisher_test_api(self) -> PublisherTestApi:
        return PublisherTestApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_api(self) -> PublisherUserApi:
        return PublisherUserApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_access_api(self) -> PublisherUserAccessApi:
        return PublisherUserAccessApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_access_active_api(self) -> PublisherUserAccessActiveApi:
        return PublisherUserAccessActiveApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_address_api(self) -> PublisherUserAddressApi:
        return PublisherUserAddressApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_app_api(self) -> PublisherUserAppApi:
        return PublisherUserAppApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_billing_address_api(self) -> PublisherUserBillingAddressApi:
        return PublisherUserBillingAddressApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_bulk_import_api(self) -> PublisherUserBulkImportApi:
        return PublisherUserBulkImportApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_email_api(self) -> PublisherUserEmailApi:
        return PublisherUserEmailApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_list_api(self) -> PublisherUserListApi:
        return PublisherUserListApi(self.config, self.http_callback)

    @cached_property
    def publisher_user_note_api(self) -> PublisherUserNoteApi:
        return PublisherUserNoteApi(self.config, self.http_callback)

    @cached_property
    def publisher_voucher_api(self) -> PublisherVoucherApi:
        return PublisherVoucherApi(self.config, self.http_callback)

    @cached_property
    def publisher_webhook_api(self) -> PublisherWebhookApi:
        return PublisherWebhookApi(self.config, self.http_callback)

    @cached_property
    def publisher_webhook_response_api(self) -> PublisherWebhookResponseApi:
        return PublisherWebhookResponseApi(self.config, self.http_callback)

    @cached_property
    def publisher_webhook_settings_api(self) -> PublisherWebhookSettingsApi:
        return PublisherWebhookSettingsApi(self.config, self.http_callback)

    @cached_property
    def access_api(self) -> AccessApi:
        return AccessApi(self.config, self.http_callback)

    @cached_property
    def access_token_api(self) -> AccessTokenApi:
        return AccessTokenApi(self.config, self.http_callback)

    @cached_property
    def anon_assets_api(self) -> AnonAssetsApi:
        return AnonAssetsApi(self.config, self.http_callback)

    @cached_property
    def anon_country_list_api(self) -> AnonCountryListApi:
        return AnonCountryListApi(self.config, self.http_callback)

    @cached_property
    def anon_error_api(self) -> AnonErrorApi:
        return AnonErrorApi(self.config, self.http_callback)

    @cached_property
    def anon_mobile_sdk_id_deployment_api(self) -> AnonMobileSdkIdDeploymentApi:
        return AnonMobileSdkIdDeploymentApi(self.config, self.http_callback)

    @cached_property
    def anon_user_api(self) -> AnonUserApi:
        return AnonUserApi(self.config, self.http_callback)

    @cached_property
    def anon_user_disable_api(self) -> AnonUserDisableApi:
        return AnonUserDisableApi(self.config, self.http_callback)

    @cached_property
    def conversion_api(self) -> ConversionApi:
        return ConversionApi(self.config, self.http_callback)

    @cached_property
    def conversion_external_api(self) -> ConversionExternalApi:
        return ConversionExternalApi(self.config, self.http_callback)

    @cached_property
    def conversion_registration_api(self) -> ConversionRegistrationApi:
        return ConversionRegistrationApi(self.config, self.http_callback)

    @cached_property
    def email_confirmation_api(self) -> EmailConfirmationApi:
        return EmailConfirmationApi(self.config, self.http_callback)

    @cached_property
    def exposure_api(self) -> ExposureApi:
        return ExposureApi(self.config, self.http_callback)

    @cached_property
    def oauth_api(self) -> OauthApi:
        return OauthApi(self.config, self.http_callback)

    @cached_property
    def subscription_api(self) -> SubscriptionApi:
        return SubscriptionApi(self.config, self.http_callback)

    @cached_property
    def swg_sync_api(self) -> SwgSyncApi:
        return SwgSyncApi(self.config, self.http_callback)

    @cached_property
    def identity_api(self) -> IdentityApi:
        return IdentityApi(self.config, self.http_callback)

    @cached_property
    def identity_oauth_api(self) -> IdentityOauthApi:
        return IdentityOauthApi(self.config, self.http_callback)

    @cached_property
    def identity_token_api(self) -> IdentityTokenApi:
        return IdentityTokenApi(self.config, self.http_callback)

    @cached_property
    def publisher_api(self) -> PublisherApi:
        return PublisherApi(self.config, self.http_callback)

    @cached_property
    def publisher_audit_api(self) -> PublisherAuditApi:
        return PublisherAuditApi(self.config, self.http_callback)

    @cached_property
    def publisher_form_api(self) -> PublisherFormApi:
        return PublisherFormApi(self.config, self.http_callback)

    @cached_property
    def publisher_identity_api(self) -> PublisherIdentityApi:
        return PublisherIdentityApi(self.config, self.http_callback)

    @cached_property
    def publisher_identity_doi_api(self) -> PublisherIdentityDoiApi:
        return PublisherIdentityDoiApi(self.config, self.http_callback)

    @cached_property
    def publisher_identity_session_api(self) -> PublisherIdentitySessionApi:
        return PublisherIdentitySessionApi(self.config, self.http_callback)

    @cached_property
    def publisher_identity_set_api(self) -> PublisherIdentitySetApi:
        return PublisherIdentitySetApi(self.config, self.http_callback)

    @cached_property
    def publisher_import_custom_fields_api(self) -> PublisherImportCustomFieldsApi:
        return PublisherImportCustomFieldsApi(self.config, self.http_callback)

    @cached_property
    def publisher_link_api(self) -> PublisherLinkApi:
        return PublisherLinkApi(self.config, self.http_callback)

    @cached_property
    def publisher_login_api(self) -> PublisherLoginApi:
        return PublisherLoginApi(self.config, self.http_callback)

    @cached_property
    def publisher_login_social_api(self) -> PublisherLoginSocialApi:
        return PublisherLoginSocialApi(self.config, self.http_callback)

    @cached_property
    def publisher_reset_api(self) -> PublisherResetApi:
        return PublisherResetApi(self.config, self.http_callback)

    @cached_property
    def publisher_social_api(self) -> PublisherSocialApi:
        return PublisherSocialApi(self.config, self.http_callback)

    @cached_property
    def publisher_token_api(self) -> PublisherTokenApi:
        return PublisherTokenApi(self.config, self.http_callback)

    @cached_property
    def publisher_userinfo_api(self) -> PublisherUserinfoApi:
        return PublisherUserinfoApi(self.config, self.http_callback)

    @cached_property
    def publisher_users_api(self) -> PublisherUsersApi:
        return PublisherUsersApi(self.config, self.http_callback)

