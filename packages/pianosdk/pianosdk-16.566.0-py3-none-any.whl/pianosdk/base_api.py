from pianosdk.constants import USER_AGENT
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.httpwrap import HttpRequest, HttpResponse


class BaseApi:
    global_headers = {
        'user-agent': USER_AGENT
    }

    def __init__(self, config: Configuration, http_callback: HttpCallBack = None):
        self._config = config
        self._http_callback = http_callback

    @property
    def config(self):
        return self._config

    @property
    def http_callback(self):
        return self._http_callback

    def _execute_request(self, request: HttpRequest) -> HttpResponse:
        if self.http_callback is not None:
            self.http_callback.on_before_request(request)
        temp = self.global_headers.copy()
        temp.update(request.headers)
        request.headers = temp

        if self.config.additional_headers is not None:
            request.headers.update(self.config.additional_headers)

        response = self.config.http_client.execute(request)

        if self.http_callback is not None:
            self.http_callback.on_after_response(response)

        return response
