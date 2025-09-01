from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from typing import Any
from pianosdk.publisher.models.user import User


class PublisherUserApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create(self, aid: str, uid: str, email: str, first_name: str = None, last_name: str = None, create_from_external: bool = None) -> ApiResponse[User]:
        _url_path = '/api/v3/publisher/user/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'email': _encode_parameter(email),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name),
            'create_from_external': _encode_parameter(create_from_external)
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
        _result = _json_deserialize(_response, User)
        return _result

    def disable(self, aid: str, uid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/user/disable'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid)
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
        _result = _json_deserialize(_response)
        return _result

    def get(self, aid: str, uid: str, disabled: bool = False) -> ApiResponse[User]:
        _url_path = '/api/v3/publisher/user/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'disabled': _encode_parameter(disabled)
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
        _result = _json_deserialize(_response, User)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, disabled: bool = False, q: str = None, search_after: str = None, esdebug: bool = False) -> ApiResponse[List[User]]:
        _url_path = '/api/v3/publisher/user/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'disabled': _encode_parameter(disabled),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'search_after': _encode_parameter(search_after),
            'esdebug': _encode_parameter(esdebug)
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
        _result = _json_deserialize(_response, User)
        return _result

    def register(self, aid: str, email: str = None, first_name: str = None, last_name: str = None) -> ApiResponse[User]:
        _url_path = '/api/v3/publisher/user/register'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'email': _encode_parameter(email),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name)
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
        _result = _json_deserialize(_response, User)
        return _result

    def search(self, aid: str, offset: int = 0, limit: int = 100, uid: str = None, exclude_cf_metadata: bool = False, name: str = None, email: str = None, registered_from: datetime = None, registered_until: datetime = None, access_to_resources: List[str] = None, converted_terms: List[str] = None, access_from: datetime = None, access_until: datetime = None, converted_term_from: datetime = None, converted_term_until: datetime = None, converted_term_sharing_type: str = None, redeemed_promotions: List[str] = None, redeemed_promotion_from: datetime = None, redeemed_promotion_until: datetime = None, trial_period_is_active: bool = None, has_trial_period: bool = None, has_access: bool = None, has_conversion_term: bool = None, has_redeemed_promotion: bool = None, include_trial_redemptions: bool = None, converted_term_types: List[str] = None, has_conversion_term_type: bool = None, spent_money_currency: str = None, spent_money_from: float = None, spent_money_until: float = None, spent_from_date: datetime = None, spent_until_date: datetime = None, payment_methods: List[int] = None, billing_failure_from: datetime = None, billing_failure_until: datetime = None, had_billing_failure: bool = None, has_payment: bool = None, upi_ext_customer_id: str = None, credit_card_will_expire: str = None, active_subscription_to_resources: List[str] = None, has_active_subscription: bool = None, subscription_start_from: datetime = None, subscription_start_until: datetime = None, subscription_renew_from: datetime = None, subscription_renew_until: datetime = None, subscription_expire_from: datetime = None, subscription_expire_until: datetime = None, trial_expire_from: datetime = None, trial_expire_until: datetime = None, has_any_subscriptions: bool = None, has_subscription_will_renew: bool = None, has_subscription_will_expire: bool = None, has_subscription_starts: bool = None, has_unresolved_inquiry: bool = None, submitted_inquiry_from: datetime = None, submitted_inquiry_until: datetime = None, received_response_from: datetime = None, received_response_until: datetime = None, resolved_inquiry_from: datetime = None, resolved_inquiry_until: datetime = None, has_submitted_inquiry: bool = None, has_received_response_inquiry: bool = None, has_resolved_inquiry: bool = None, has_licensing_contract_redemptions: bool = None, selected_licensees: List[str] = None, selected_contracts: List[str] = None, licensing_contract_redeemed_from: datetime = None, licensing_contract_redeemed_until: datetime = None, data_type: List[str] = None, data: str = None, has_data: bool = None, has_last_access_time: bool = None, last_access_time_from: datetime = None, last_access_time_until: datetime = None, selected_consents_map: List[str] = None, consent_checked: bool = None, custom_fields: str = None, source: str = None, invert_credit_card_will_expire: bool = None, has_email_confirmation_required: bool = None, email_confirmation_state: str = None, consent_has_data: bool = None, order_by: str = None, order_direction: str = None, q: str = None, search_after: str = None, esdebug: bool = False) -> ApiResponse[List[User]]:
        _url_path = '/api/v3/publisher/user/search'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'exclude_cf_metadata': _encode_parameter(exclude_cf_metadata),
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
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'search_after': _encode_parameter(search_after),
            'esdebug': _encode_parameter(esdebug)
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
        _result = _json_deserialize(_response, User)
        return _result

    def update(self, aid: str, uid: str, email: str = None, first_name: str = None, last_name: str = None, custom_fields: Any = None) -> ApiResponse[User]:
        _url_path = '/api/v3/publisher/user/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'email': _encode_parameter(email),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name)
        }

        _body = custom_fields and custom_fields.dict()
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, User)
        return _result

