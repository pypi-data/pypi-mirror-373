from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter


class PublisherLinkApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def link_social(self, aid: str, uid: str, social_type: str, redirect_uri: str, ab_test_ids: List[str] = None, affiliate: bool = None, response_type: str = None, authorization: str = None, form_id: str = None) -> ApiResponse[Dict]:
        _url_path = '/id/api/v1/publisher/link/social'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'social_type': _encode_parameter(social_type),
            'redirect_uri': _encode_parameter(redirect_uri),
            'ab_test_ids': _encode_parameter(ab_test_ids),
            'affiliate': _encode_parameter(affiliate),
            'response_type': _encode_parameter(response_type),
            'form_id': _encode_parameter(form_id)
        }

        _headers = {
            'Authorization': authorization,
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

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

