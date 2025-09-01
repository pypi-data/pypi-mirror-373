from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.contract_user import ContractUser


class PublisherLicensingContractUserApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_contract_user(self, aid: str, contract_id: str, email: str, first_name: str = None, last_name: str = None, contract_user_session_id: str = None) -> ApiResponse[ContractUser]:
        _url_path = '/api/v3/publisher/licensing/contractUser/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'email': _encode_parameter(email),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name),
            'contract_user_session_id': _encode_parameter(contract_user_session_id)
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
        _result = _json_deserialize(_response, ContractUser)
        return _result

    def get_contract_user_list(self, aid: str, contract_id: str, offset: int = 0, limit: int = 100, order_by: str = 'email', order_direction: str = None, status_list: List[str] = None, q: str = None) -> ApiResponse[List[ContractUser]]:
        _url_path = '/api/v3/publisher/licensing/contractUser/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'status_list': _encode_parameter(status_list),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit)
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
        _result = _json_deserialize(_response, ContractUser)
        return _result

    def invite_contract_users(self, aid: str, contract_id: str, contract_user_session_id: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractUser/invite'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'contract_user_session_id': _encode_parameter(contract_user_session_id)
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

    def remove_and_revoke_contract_user(self, aid: str, contract_id: str, contract_user_id: str, contract_user_session_id: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractUser/removeAndRevoke'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'contract_user_id': _encode_parameter(contract_user_id),
            'contract_user_session_id': _encode_parameter(contract_user_session_id)
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

    def remove_contract_user(self, aid: str, contract_id: str, contract_user_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractUser/remove'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'contract_user_id': _encode_parameter(contract_user_id)
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

    def restore_contract_user(self, aid: str, contract_id: str, contract_user_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractUser/restore'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'contract_user_id': _encode_parameter(contract_user_id)
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

    def revoke_contract_user(self, aid: str, contract_id: str, contract_user_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractUser/revoke'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'contract_user_id': _encode_parameter(contract_user_id)
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

    def update_contract_user(self, aid: str, contract_id: str, contract_user_id: str, email: str, first_name: str = None, last_name: str = None, contract_user_session_id: str = None) -> ApiResponse[ContractUser]:
        _url_path = '/api/v3/publisher/licensing/contractUser/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'contract_user_id': _encode_parameter(contract_user_id),
            'email': _encode_parameter(email),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name),
            'contract_user_session_id': _encode_parameter(contract_user_session_id)
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
        _result = _json_deserialize(_response, ContractUser)
        return _result

