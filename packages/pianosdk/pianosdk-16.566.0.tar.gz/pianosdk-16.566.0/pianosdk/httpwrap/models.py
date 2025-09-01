from typing import Dict, MutableMapping


class HttpRequest:
    """Information about an HTTP Request including its method, headers,
        parameters, URL, and Basic Auth details
    """

    def __init__(self,
                 http_method: str,
                 query_url: str,
                 headers: Dict = None,
                 query_parameters: Dict = None,
                 parameters: Dict = None,
                 json: Dict = None,
                 files: Dict = None):
        """Constructor for the HttpRequest class
        Args:
            http_method (HttpMethodEnum): The HTTP Method.
            query_url (string): The URL to send the request to.
            headers (dict, optional): The headers for the HTTP Request.
            query_parameters (dict, optional): Query parameters to add in the
                URL.
            parameters (dict, optional): Form or body parameters to be included
                in the body.
            json (dict, optional): Body parameters to be included
                in the body as JSON.
            files (dict, optional): Files to be sent with the request.
        """
        self.http_method = http_method
        self.query_url = query_url
        self.headers = headers or {}
        self.query_parameters = query_parameters or {}
        self.parameters = parameters or {}
        self.json = json or {}
        self.files = files or {}

    def add_header(self, name: str, value: str):
        """ Add a header to the HttpRequest.
        Args:
            name (string): The name of the header.
            value (string): The value of the header.
        """
        self.headers[name] = value

    def add_parameter(self, name: str, value: str):
        """ Add a parameter to the HttpRequest.
        Args:
            name (string): The name of the parameter.
            value (string): The value of the parameter.
        """
        self.parameters[name] = value

    def add_query_parameter(self, name: str, value: str):
        """ Add a query parameter to the HttpRequest.
        Args:
            name (string): The name of the query parameter.
            value (string): The value of the query parameter.
        """
        self.query_parameters[name] = value


class HttpResponse:
    """Information about an HTTP Response including its status code, returned
        headers, and raw body
    """

    def __init__(self,
                 status_code: int,
                 reason_phrase: str,
                 headers: MutableMapping,
                 text: str,
                 request: HttpRequest):
        """Constructor for the HttpResponse class
        Args:
            status_code (int): The response status code.
            reason_phrase (string): The response reason phrase.
            headers (dict): The response headers.
            text (string): The raw body from the server.
            request (HttpRequest): The request that resulted in this response.
        """
        self.status_code = status_code
        self.reason_phrase = reason_phrase
        self.headers = headers
        self.text = text
        self.request = request
        self.request_id = headers.get('x-request-id', None)


class HttpCallBack:
    def on_before_request(self, request: HttpRequest):
        """The controller will call this method before making the HttpRequest.
        """
        raise NotImplementedError("This method has not been implemented.")

    def on_after_response(self, http_response: HttpResponse):
        """The controller will call this method after making the HttpRequest.
        """
        raise NotImplementedError("This method has not been implemented.")
