from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.offer_template_version import OfferTemplateVersion


class PublisherOfferTemplateCreateApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_empty(self, aid: str, name: str, description: str = None, category_id: str = None, history_comment: str = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/create/empty'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'category_id': _encode_parameter(category_id),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

