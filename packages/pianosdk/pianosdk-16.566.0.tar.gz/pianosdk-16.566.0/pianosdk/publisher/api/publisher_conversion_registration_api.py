from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term_conversion import TermConversion


class PublisherConversionRegistrationApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_registration_conversion(self, aid: str, uid: str, term_id: str, email: str, first_name: str = None, last_name: str = None, create_date: datetime = None, access_start_date: datetime = None, tbc: str = None, pageview_id: str = None) -> ApiResponse[TermConversion]:
        _url_path = '/api/v3/publisher/conversion/registration/create'
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
            'term_id': _encode_parameter(term_id),
            'email': _encode_parameter(email),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name),
            'create_date': _encode_parameter(create_date),
            'access_start_date': _encode_parameter(access_start_date),
            'tbc': _encode_parameter(tbc),
            'pageview_id': _encode_parameter(pageview_id)
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
        _result = _json_deserialize(_response, TermConversion)
        return _result

