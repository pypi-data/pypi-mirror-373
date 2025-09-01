from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.subscription_upgrade_status import SubscriptionUpgradeStatus


class PublisherTermChangeApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def can_change_term(self, subscription_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/term/change/can'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'subscription_id': _encode_parameter(subscription_id)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def cancel(self, aid: str, subscription_from: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/term/change/cancel'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_from': _encode_parameter(subscription_from)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def change(self, aid: str, uid: str, subscription_from: str, term_to: str, billing_timing: str, immediate_access: bool, prorate_access: bool, term_to_period_id: str = None, shared_accounts: str = None, user_address: str = None) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/term/change/do'
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
            'subscription_from': _encode_parameter(subscription_from),
            'term_to': _encode_parameter(term_to),
            'term_to_period_id': _encode_parameter(term_to_period_id),
            'billing_timing': _encode_parameter(billing_timing),
            'immediate_access': _encode_parameter(immediate_access),
            'prorate_access': _encode_parameter(prorate_access),
            'shared_accounts': _encode_parameter(shared_accounts),
            'user_address': _encode_parameter(user_address)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def get_subscription_upgrade_status(self, aid: str, uid: str, subscription_id: str) -> ApiResponse[SubscriptionUpgradeStatus]:
        _url_path = '/api/v3/publisher/term/change/getSubscriptionUpgradeStatus'
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
            'subscription_id': _encode_parameter(subscription_id)
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
        _result = _json_deserialize(_response, SubscriptionUpgradeStatus)
        return _result

