from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.shared_subscription import SharedSubscription


class PublisherSubscriptionShareApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def invite(self, aid: str, subscription_id: str, shared_account: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/share/invite'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'shared_account': _encode_parameter(shared_account)
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

    def list(self, aid: str, offset: int, limit: int, term_id: str = None, unused_accesses_only: bool = False, status: str = None, start_date: datetime = None, end_date: datetime = None, select_by: str = None) -> ApiResponse[List[SharedSubscription]]:
        _url_path = '/api/v3/publisher/subscription/share/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'term_id': _encode_parameter(term_id),
            'unused_accesses_only': _encode_parameter(unused_accesses_only),
            'status': _encode_parameter(status),
            'start_date': _encode_parameter(start_date),
            'end_date': _encode_parameter(end_date),
            'select_by': _encode_parameter(select_by)
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
        _result = _json_deserialize(_response, SharedSubscription)
        return _result

    def resend(self, aid: str, subscription_id: str, account_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/share/resend'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'account_id': _encode_parameter(account_id)
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

    def revoke(self, aid: str, subscription_id: str, account_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/share/revoke'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'account_id': _encode_parameter(account_id)
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

    def start(self, aid: str, subscription_id: str, shared_accounts: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/share/start'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'shared_accounts': _encode_parameter(shared_accounts)
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

    def stop(self, aid: str, subscription_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/share/stop'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
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

    def update(self, aid: str, subscription_id: str, shared_accounts: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/subscription/share/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'subscription_id': _encode_parameter(subscription_id),
            'shared_accounts': _encode_parameter(shared_accounts)
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

    def validate(self, aid: str, rid: str, email: str) -> ApiResponse[str]:
        _url_path = '/api/v3/publisher/subscription/share/validate'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'email': _encode_parameter(email)
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
        _result = _json_deserialize(_response, str)
        return _result

