from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.afc_configuration import AfcConfiguration


class PublisherAfcConfigurationApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def delete_configuration(self, aid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/afc/configuration/delete'
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
        _result = _json_deserialize(_response)
        return _result

    def get_configuration(self, aid: str) -> ApiResponse[AfcConfiguration]:
        _url_path = '/api/v3/publisher/afc/configuration/get'
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
        _result = _json_deserialize(_response, AfcConfiguration)
        return _result

    def health_check(self, aid: str, afc_client_id: str, afc_username: str, afc_password: str, afc_client_profile_id: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/afc/configuration/healthCheck'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'afc_client_id': _encode_parameter(afc_client_id),
            'afc_username': _encode_parameter(afc_username),
            'afc_password': _encode_parameter(afc_password),
            'afc_client_profile_id': _encode_parameter(afc_client_profile_id)
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
        _result = _json_deserialize(_response)
        return _result

    def save_configuration(self, aid: str, afc_client_id: str, afc_username: str, afc_password: str, load_date: str, afc_client_profile_id: str = None) -> ApiResponse[AfcConfiguration]:
        _url_path = '/api/v3/publisher/afc/configuration/save'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'afc_client_id': _encode_parameter(afc_client_id),
            'afc_username': _encode_parameter(afc_username),
            'afc_password': _encode_parameter(afc_password),
            'afc_client_profile_id': _encode_parameter(afc_client_profile_id),
            'load_date': _encode_parameter(load_date)
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
        _result = _json_deserialize(_response, AfcConfiguration)
        return _result

