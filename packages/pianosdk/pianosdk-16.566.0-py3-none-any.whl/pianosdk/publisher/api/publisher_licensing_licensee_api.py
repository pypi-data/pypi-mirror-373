from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.licensee import Licensee


class PublisherLicensingLicenseeApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def archive_licensee(self, aid: str, licensee_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/licensing/licensee/archive'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id)
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

    def create_licensee(self, aid: str, manager_uids: List[str], name: str, description: str = None, representatives: str = None, logo_url: str = None) -> ApiResponse[Licensee]:
        _url_path = '/api/v3/publisher/licensing/licensee/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'description': _encode_parameter(description),
            'manager_uids': _encode_parameter(manager_uids),
            'representatives': _encode_parameter(representatives),
            'logo_url': _encode_parameter(logo_url),
            'name': _encode_parameter(name)
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
        _result = _json_deserialize(_response, Licensee)
        return _result

    def get_licensee(self, aid: str, licensee_id: str) -> ApiResponse[Licensee]:
        _url_path = '/api/v3/publisher/licensing/licensee/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'licensee_id': _encode_parameter(licensee_id)
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
        _result = _json_deserialize(_response, Licensee)
        return _result

    def get_licensee_count(self, aid: str) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/licensing/licensee/count'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid)
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
        _result = _json_deserialize(_response, int)
        return _result

    def get_licensee_list(self, aid: str, offset: int = 0, limit: int = 100, q: str = None) -> ApiResponse[List[Licensee]]:
        _url_path = '/api/v3/publisher/licensing/licensee/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
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
        _result = _json_deserialize(_response, Licensee)
        return _result

    def update_licensee(self, aid: str, licensee_id: str, manager_uids: List[str], name: str, description: str = None, representatives: str = None, logo_url: str = None) -> ApiResponse[Licensee]:
        _url_path = '/api/v3/publisher/licensing/licensee/update'
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
            'description': _encode_parameter(description),
            'manager_uids': _encode_parameter(manager_uids),
            'representatives': _encode_parameter(representatives),
            'logo_url': _encode_parameter(logo_url),
            'name': _encode_parameter(name)
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
        _result = _json_deserialize(_response, Licensee)
        return _result

