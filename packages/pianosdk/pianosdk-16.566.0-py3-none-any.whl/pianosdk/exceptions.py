from copy import deepcopy
from typing import Dict


class ApiException(Exception):
    request_id: str
    error_code: int
    errors: Dict[str, str]
    is_transport_error: bool

    def __init__(self, request_id: str, message: str, code: int = 0, errors: Dict[str, str] = None, is_transport_error: bool = False, *args: object) -> None:
        super().__init__(message, *args)
        self.request_id = request_id
        self.error_code = code
        self.errors = errors and deepcopy(errors)
        self.is_transport_error = is_transport_error
