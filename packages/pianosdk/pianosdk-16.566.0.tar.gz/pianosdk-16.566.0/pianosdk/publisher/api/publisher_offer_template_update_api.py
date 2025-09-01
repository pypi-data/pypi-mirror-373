from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.offer_template_version import OfferTemplateVersion


class PublisherOfferTemplateUpdateApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def update_content_fields(self, aid: str, offer_template_id: str, content_field_list: str, variant_list: str, history_comment: str = None, is_validate: bool = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/update/contentfields'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'content_field_list': _encode_parameter(content_field_list),
            'variant_list': _encode_parameter(variant_list),
            'history_comment': _encode_parameter(history_comment),
            'is_validate': _encode_parameter(is_validate)
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

