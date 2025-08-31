from typing import Mapping, Text

from requests import models
from requests.adapters import HTTPAdapter

PreparedRequest = models.PreparedRequest
Response = models.Response

class TimeoutHTTPAdapter(HTTPAdapter):
    def send(
        self,
        request: PreparedRequest,
        stream: bool = ...,
        timeout: None | float | tuple[float, float] | tuple[float, None] = ...,
        verify: bool | str = ...,
        cert: None | bytes | Text | tuple[bytes | Text, bytes | Text] = ...,
        proxies: Mapping[str, str] | None = ...,
    ) -> Response: ...
