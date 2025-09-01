from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter


class ExposureApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def log(self, aid: str, tracking_id: str, browser_id: str, user_token: str = None, page_title: str = None, url: str = None, referer: str = None, content_author: str = None, content_created: str = None, content_section: str = None, content_type: str = None, tags: List[str] = None, previous_user_segments: str = None, user_state: str = None, cookie_consents: str = None, previous_user_segments2: str = None, custom_params: str = None, external_offer_id: str = None, external_template_id: str = None, external_term_ids: List[str] = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/exposure/log'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'tracking_id': _encode_parameter(tracking_id),
            'browser_id': _encode_parameter(browser_id),
            'user_token': _encode_parameter(user_token),
            'page_title': _encode_parameter(page_title),
            'url': _encode_parameter(url),
            'referer': _encode_parameter(referer),
            'content_author': _encode_parameter(content_author),
            'content_created': _encode_parameter(content_created),
            'content_section': _encode_parameter(content_section),
            'content_type': _encode_parameter(content_type),
            'tags': _encode_parameter(tags),
            'previous_user_segments': _encode_parameter(previous_user_segments),
            'user_state': _encode_parameter(user_state),
            'cookie_consents': _encode_parameter(cookie_consents),
            'previous_user_segments': _encode_parameter(previous_user_segments2),
            'custom_params': _encode_parameter(custom_params),
            'external_offer_id': _encode_parameter(external_offer_id),
            'external_template_id': _encode_parameter(external_template_id),
            'external_term_ids': _encode_parameter(external_term_ids)
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

