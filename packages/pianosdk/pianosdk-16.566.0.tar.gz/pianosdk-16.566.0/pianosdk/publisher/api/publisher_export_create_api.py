from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.export import Export


class PublisherExportCreateApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_access_report_export(self, aid: str, export_name: str, date_from: datetime, date_to: datetime, access_status: str = 'ALL', term_type: List[str] = None, term_id: List[str] = None, next_billing_date: datetime = None, last_payment_status: str = None, end_date_from: datetime = None, end_date_to: datetime = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/accessReportExport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'access_status': _encode_parameter(access_status),
            'term_type': _encode_parameter(term_type),
            'term_id': _encode_parameter(term_id),
            'next_billing_date': _encode_parameter(next_billing_date),
            'last_payment_status': _encode_parameter(last_payment_status),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to),
            'end_date_from': _encode_parameter(end_date_from),
            'end_date_to': _encode_parameter(end_date_to)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_daily_activity_report_export(self, aid: str, export_name: str, _date: datetime, term_type: List[str] = None, currency: str = None, currency_list: List[str] = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/dailyActivityReportExport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'date': _encode_parameter(_date),
            'term_type': _encode_parameter(term_type),
            'currency': _encode_parameter(currency),
            'currencyList': _encode_parameter(currency_list)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_monthly_activity_report_export(self, aid: str, export_name: str, month: int, year: int, term_type: List[str] = None, currency: str = None, currency_list: List[str] = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/monthlyActivityReportExport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'month': _encode_parameter(month),
            'year': _encode_parameter(year),
            'term_type': _encode_parameter(term_type),
            'currency': _encode_parameter(currency),
            'currencyList': _encode_parameter(currency_list)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_subscription_detailed_report(self, aid: str, export_name: str, q: str = None, search_new_subscriptions: bool = None, new_subscriptions_created_from: datetime = None, new_subscriptions_created_to: datetime = None, search_active_now_subscriptions: bool = None, active_now_subscriptions_statuses: List[str] = None, search_inactive_subscriptions: bool = None, inactive_subscriptions_statuses: List[str] = None, subscriptions_inactive_from: datetime = None, subscriptions_inactive_to: datetime = None, search_updated_subscriptions: bool = None, updated_subscriptions_statuses: List[str] = None, subscriptions_updated_from: datetime = None, subscriptions_updated_to: datetime = None, search_auto_renewing_subscriptions: bool = None, subscriptions_auto_renewing: bool = None, search_subscriptions_by_next_billing_date: bool = None, subscriptions_next_billing_date_from: datetime = None, subscriptions_next_billing_date_to: datetime = None, search_subscriptions_by_terms: bool = None, subscriptions_terms: List[str] = None, subscriptions_term_types: List[str] = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/subscriptionDetailsReport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'q': _encode_parameter(q),
            'search_new_subscriptions': _encode_parameter(search_new_subscriptions),
            'new_subscriptions_created_from': _encode_parameter(new_subscriptions_created_from),
            'new_subscriptions_created_to': _encode_parameter(new_subscriptions_created_to),
            'search_active_now_subscriptions': _encode_parameter(search_active_now_subscriptions),
            'active_now_subscriptions_statuses': _encode_parameter(active_now_subscriptions_statuses),
            'search_inactive_subscriptions': _encode_parameter(search_inactive_subscriptions),
            'inactive_subscriptions_statuses': _encode_parameter(inactive_subscriptions_statuses),
            'subscriptions_inactive_from': _encode_parameter(subscriptions_inactive_from),
            'subscriptions_inactive_to': _encode_parameter(subscriptions_inactive_to),
            'search_updated_subscriptions': _encode_parameter(search_updated_subscriptions),
            'updated_subscriptions_statuses': _encode_parameter(updated_subscriptions_statuses),
            'subscriptions_updated_from': _encode_parameter(subscriptions_updated_from),
            'subscriptions_updated_to': _encode_parameter(subscriptions_updated_to),
            'search_auto_renewing_subscriptions': _encode_parameter(search_auto_renewing_subscriptions),
            'subscriptions_auto_renewing': _encode_parameter(subscriptions_auto_renewing),
            'search_subscriptions_by_next_billing_date': _encode_parameter(search_subscriptions_by_next_billing_date),
            'subscriptions_next_billing_date_from': _encode_parameter(subscriptions_next_billing_date_from),
            'subscriptions_next_billing_date_to': _encode_parameter(subscriptions_next_billing_date_to),
            'search_subscriptions_by_terms': _encode_parameter(search_subscriptions_by_terms),
            'subscriptions_terms': _encode_parameter(subscriptions_terms),
            'subscriptions_term_types': _encode_parameter(subscriptions_term_types)
        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_subscription_summary_report(self, aid: str, export_name: str, date_from: datetime, date_to: datetime) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/subscriptionSummaryReport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to)
        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_term_change_report_export(self, aid: str, export_name: str, date_from: datetime = None, date_to: datetime = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/termChangeReportExport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_transactions_report(self, aid: str, export_name: str, transactions_type: str = 'purchases', order_by: str = 'payment_date', order_direction: str = 'desc', q: str = None, date_from: datetime = None, date_to: datetime = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/transactionsReport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'transactions_type': _encode_parameter(transactions_type),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'q': _encode_parameter(q),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to)
        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

    def create_user_export(self, aid: str, export_name: str, export_custom_fields: List[str] = None, export_all_custom_fields: bool = False, include_notes: bool = None, name: str = None, email: str = None, registered_from: datetime = None, registered_until: datetime = None, access_to_resources: List[str] = None, converted_terms: List[str] = None, access_from: datetime = None, access_until: datetime = None, converted_term_from: datetime = None, converted_term_until: datetime = None, converted_term_sharing_type: str = None, redeemed_promotions: List[str] = None, redeemed_promotion_from: datetime = None, redeemed_promotion_until: datetime = None, trial_period_is_active: bool = None, has_trial_period: bool = None, has_access: bool = None, has_conversion_term: bool = None, has_redeemed_promotion: bool = None, include_trial_redemptions: bool = None, converted_term_types: List[str] = None, has_conversion_term_type: bool = None, spent_money_currency: str = None, spent_money_from: float = None, spent_money_until: float = None, spent_from_date: datetime = None, spent_until_date: datetime = None, payment_methods: List[int] = None, billing_failure_from: datetime = None, billing_failure_until: datetime = None, had_billing_failure: bool = None, has_payment: bool = None, upi_ext_customer_id: str = None, credit_card_will_expire: str = None, active_subscription_to_resources: List[str] = None, has_active_subscription: bool = None, subscription_start_from: datetime = None, subscription_start_until: datetime = None, subscription_renew_from: datetime = None, subscription_renew_until: datetime = None, subscription_expire_from: datetime = None, subscription_expire_until: datetime = None, trial_expire_from: datetime = None, trial_expire_until: datetime = None, has_any_subscriptions: bool = None, has_subscription_will_renew: bool = None, has_subscription_will_expire: bool = None, has_subscription_starts: bool = None, has_unresolved_inquiry: bool = None, submitted_inquiry_from: datetime = None, submitted_inquiry_until: datetime = None, received_response_from: datetime = None, received_response_until: datetime = None, resolved_inquiry_from: datetime = None, resolved_inquiry_until: datetime = None, has_submitted_inquiry: bool = None, has_received_response_inquiry: bool = None, has_resolved_inquiry: bool = None, has_licensing_contract_redemptions: bool = None, selected_licensees: List[str] = None, selected_contracts: List[str] = None, licensing_contract_redeemed_from: datetime = None, licensing_contract_redeemed_until: datetime = None, data_type: List[str] = None, data: str = None, has_data: bool = None, has_last_access_time: bool = None, last_access_time_from: datetime = None, last_access_time_until: datetime = None, selected_consents_map: List[str] = None, consent_checked: bool = None, custom_fields: str = None, source: str = None, invert_credit_card_will_expire: bool = None, has_email_confirmation_required: bool = None, email_confirmation_state: str = None, consent_has_data: bool = None, q: str = None, order_by: str = None, order_direction: str = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/userExport'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'export_custom_fields': _encode_parameter(export_custom_fields),
            'export_all_custom_fields': _encode_parameter(export_all_custom_fields),
            'include_notes': _encode_parameter(include_notes),
            'name': _encode_parameter(name),
            'email': _encode_parameter(email),
            'registered_from': _encode_parameter(registered_from),
            'registered_until': _encode_parameter(registered_until),
            'access_to_resources': _encode_parameter(access_to_resources),
            'converted_terms': _encode_parameter(converted_terms),
            'access_from': _encode_parameter(access_from),
            'access_until': _encode_parameter(access_until),
            'converted_term_from': _encode_parameter(converted_term_from),
            'converted_term_until': _encode_parameter(converted_term_until),
            'converted_term_sharing_type': _encode_parameter(converted_term_sharing_type),
            'redeemed_promotions': _encode_parameter(redeemed_promotions),
            'redeemed_promotion_from': _encode_parameter(redeemed_promotion_from),
            'redeemed_promotion_until': _encode_parameter(redeemed_promotion_until),
            'trial_period_is_active': _encode_parameter(trial_period_is_active),
            'has_trial_period': _encode_parameter(has_trial_period),
            'has_access': _encode_parameter(has_access),
            'has_conversion_term': _encode_parameter(has_conversion_term),
            'has_redeemed_promotion': _encode_parameter(has_redeemed_promotion),
            'include_trial_redemptions': _encode_parameter(include_trial_redemptions),
            'converted_term_types': _encode_parameter(converted_term_types),
            'has_conversion_term_type': _encode_parameter(has_conversion_term_type),
            'spent_money_currency': _encode_parameter(spent_money_currency),
            'spent_money_from': _encode_parameter(spent_money_from),
            'spent_money_until': _encode_parameter(spent_money_until),
            'spent_from_date': _encode_parameter(spent_from_date),
            'spent_until_date': _encode_parameter(spent_until_date),
            'payment_methods': _encode_parameter(payment_methods),
            'billing_failure_from': _encode_parameter(billing_failure_from),
            'billing_failure_until': _encode_parameter(billing_failure_until),
            'had_billing_failure': _encode_parameter(had_billing_failure),
            'has_payment': _encode_parameter(has_payment),
            'upi_ext_customer_id': _encode_parameter(upi_ext_customer_id),
            'credit_card_will_expire': _encode_parameter(credit_card_will_expire),
            'active_subscription_to_resources': _encode_parameter(active_subscription_to_resources),
            'has_active_subscription': _encode_parameter(has_active_subscription),
            'subscription_start_from': _encode_parameter(subscription_start_from),
            'subscription_start_until': _encode_parameter(subscription_start_until),
            'subscription_renew_from': _encode_parameter(subscription_renew_from),
            'subscription_renew_until': _encode_parameter(subscription_renew_until),
            'subscription_expire_from': _encode_parameter(subscription_expire_from),
            'subscription_expire_until': _encode_parameter(subscription_expire_until),
            'trial_expire_from': _encode_parameter(trial_expire_from),
            'trial_expire_until': _encode_parameter(trial_expire_until),
            'has_any_subscriptions': _encode_parameter(has_any_subscriptions),
            'has_subscription_will_renew': _encode_parameter(has_subscription_will_renew),
            'has_subscription_will_expire': _encode_parameter(has_subscription_will_expire),
            'has_subscription_starts': _encode_parameter(has_subscription_starts),
            'has_unresolved_inquiry': _encode_parameter(has_unresolved_inquiry),
            'submitted_inquiry_from': _encode_parameter(submitted_inquiry_from),
            'submitted_inquiry_until': _encode_parameter(submitted_inquiry_until),
            'received_response_from': _encode_parameter(received_response_from),
            'received_response_until': _encode_parameter(received_response_until),
            'resolved_inquiry_from': _encode_parameter(resolved_inquiry_from),
            'resolved_inquiry_until': _encode_parameter(resolved_inquiry_until),
            'has_submitted_inquiry': _encode_parameter(has_submitted_inquiry),
            'has_received_response_inquiry': _encode_parameter(has_received_response_inquiry),
            'has_resolved_inquiry': _encode_parameter(has_resolved_inquiry),
            'has_licensing_contract_redemptions': _encode_parameter(has_licensing_contract_redemptions),
            'selected_licensees': _encode_parameter(selected_licensees),
            'selected_contracts': _encode_parameter(selected_contracts),
            'licensing_contract_redeemed_from': _encode_parameter(licensing_contract_redeemed_from),
            'licensing_contract_redeemed_until': _encode_parameter(licensing_contract_redeemed_until),
            'data_type': _encode_parameter(data_type),
            'data': _encode_parameter(data),
            'has_data': _encode_parameter(has_data),
            'has_last_access_time': _encode_parameter(has_last_access_time),
            'last_access_time_from': _encode_parameter(last_access_time_from),
            'last_access_time_until': _encode_parameter(last_access_time_until),
            'selected_consents_map': _encode_parameter(selected_consents_map),
            'consent_checked': _encode_parameter(consent_checked),
            'custom_fields': _encode_parameter(custom_fields),
            'source': _encode_parameter(source),
            'invert_credit_card_will_expire': _encode_parameter(invert_credit_card_will_expire),
            'has_emailConfirmation_required': _encode_parameter(has_email_confirmation_required),
            'email_confirmation_state': _encode_parameter(email_confirmation_state),
            'consent_has_data': _encode_parameter(consent_has_data),
            'q': _encode_parameter(q),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction)
        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Export)
        return _result

