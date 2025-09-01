from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.contract import Contract


class PublisherLicensingContractApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def activate_contract(self, aid: str, contract_id: str) -> ApiResponse[Contract]:
        _url_path = '/api/v3/publisher/licensing/contract/activate'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id)
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
        _result = _json_deserialize(_response, Contract)
        return _result

    def archive_contract(self, aid: str, contract_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/contract/archive'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id)
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

    def create_contract(self, aid: str, licensee_id: str, contract_type: str, contract_name: str, seats_number: int, is_hard_seats_limit_type: bool, rid: str, landing_page_url: str = None) -> ApiResponse[Contract]:
        _url_path = '/api/v3/publisher/licensing/contract/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id),
            'contract_type': _encode_parameter(contract_type),
            'contract_name': _encode_parameter(contract_name),
            'seats_number': _encode_parameter(seats_number),
            'is_hard_seats_limit_type': _encode_parameter(is_hard_seats_limit_type),
            'rid': _encode_parameter(rid),
            'landing_page_url': _encode_parameter(landing_page_url)
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
        _result = _json_deserialize(_response, Contract)
        return _result

    def deactivate_contract(self, aid: str, contract_id: str) -> ApiResponse[Contract]:
        _url_path = '/api/v3/publisher/licensing/contract/deactivate'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id)
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
        _result = _json_deserialize(_response, Contract)
        return _result

    def get_contract(self, aid: str, contract_id: str) -> ApiResponse[Contract]:
        _url_path = '/api/v3/publisher/licensing/contract/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'contract_id': _encode_parameter(contract_id)
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
        _result = _json_deserialize(_response, Contract)
        return _result

    def get_contract_list(self, aid: str, licensee_id: str, offset: int = 0, limit: int = 100, q: str = None) -> ApiResponse[List[Contract]]:
        _url_path = '/api/v3/publisher/licensing/contract/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id),
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
        _result = _json_deserialize(_response, Contract)
        return _result

    def redeem_contract(self, aid: str, contract_id: str, uid: str) -> ApiResponse[str]:
        _url_path = '/api/v3/publisher/licensing/contract/redeem'
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
        _result = _json_deserialize(_response, str)
        return _result

    def update_contract(self, aid: str, licensee_id: str, contract_type: str, contract_id: str, contract_name: str, seats_number: int, is_hard_seats_limit_type: bool, rid: str, landing_page_url: str, contract_description: str = None, schedule_id: str = None) -> ApiResponse[Contract]:
        _url_path = '/api/v3/publisher/licensing/contract/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id),
            'contract_type': _encode_parameter(contract_type),
            'contract_id': _encode_parameter(contract_id),
            'contract_name': _encode_parameter(contract_name),
            'contract_description': _encode_parameter(contract_description),
            'seats_number': _encode_parameter(seats_number),
            'is_hard_seats_limit_type': _encode_parameter(is_hard_seats_limit_type),
            'rid': _encode_parameter(rid),
            'landing_page_url': _encode_parameter(landing_page_url),
            'schedule_id': _encode_parameter(schedule_id)
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
        _result = _json_deserialize(_response, Contract)
        return _result

