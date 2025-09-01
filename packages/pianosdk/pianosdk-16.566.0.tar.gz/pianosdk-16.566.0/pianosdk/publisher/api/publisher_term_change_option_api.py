from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term_change_option import TermChangeOption


class PublisherTermChangeOptionApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create(self, aid: str, from_term_id: str, to_term_id: str, billing_timing: str, immediate_access: bool, prorate_access: bool, description: str = None, to_period_id: str = None, from_period_id: str = None) -> ApiResponse[TermChangeOption]:
        _url_path = '/api/v3/publisher/term/change/option/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'from_term_id': _encode_parameter(from_term_id),
            'to_term_id': _encode_parameter(to_term_id),
            'billing_timing': _encode_parameter(billing_timing),
            'immediate_access': _encode_parameter(immediate_access),
            'prorate_access': _encode_parameter(prorate_access),
            'description': _encode_parameter(description),
            'to_period_id': _encode_parameter(to_period_id),
            'from_period_id': _encode_parameter(from_period_id)
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
        _result = _json_deserialize(_response, TermChangeOption)
        return _result

