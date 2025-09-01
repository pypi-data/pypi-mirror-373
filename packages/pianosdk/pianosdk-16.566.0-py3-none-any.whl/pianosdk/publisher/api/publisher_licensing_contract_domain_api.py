from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.contract_domain import ContractDomain


class PublisherLicensingContractDomainApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_contract_domain(self, aid: str, contract_id: str, contract_domain_value: str) -> ApiResponse[ContractDomain]:
        _url_path = '/api/v3/publisher/licensing/contractDomain/create'
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
            'contract_domain_value': _encode_parameter(contract_domain_value)
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
        _result = _json_deserialize(_response, ContractDomain)
        return _result

    def get_contract_domain_list(self, aid: str, contract_id: str, offset: int = 0, limit: int = 100, order_by: str = 'domain', order_direction: str = None, q: str = None) -> ApiResponse[List[ContractDomain]]:
        _url_path = '/api/v3/publisher/licensing/contractDomain/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
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
        _result = _json_deserialize(_response, ContractDomain)
        return _result

    def remove_and_revoke_contract_domain(self, aid: str, contract_id: str, contract_domain_id: str, contract_user_session_id: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractDomain/removeAndRevoke'
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
            'contract_domain_id': _encode_parameter(contract_domain_id),
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

    def remove_contract_domain(self, aid: str, contract_id: str, contract_domain_id: str, contract_user_session_id: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contractDomain/remove'
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
            'contract_domain_id': _encode_parameter(contract_domain_id),
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

    def update_contract_domain(self, aid: str, contract_id: str, contract_domain_id: str, contract_domain_value: str) -> ApiResponse[ContractDomain]:
        _url_path = '/api/v3/publisher/licensing/contractDomain/update'
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
            'contract_domain_id': _encode_parameter(contract_domain_id),
            'contract_domain_value': _encode_parameter(contract_domain_value)
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
        _result = _json_deserialize(_response, ContractDomain)
        return _result

