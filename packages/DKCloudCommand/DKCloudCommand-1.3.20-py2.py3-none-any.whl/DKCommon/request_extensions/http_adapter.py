import logging
from typing import Union

from requests.adapters import HTTPAdapter

from .settings import REQUESTS_TIMEOUT

LOG = logging.getLogger(__name__)


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    An HTTPAdapter for request sessions that automatically includes a timeout.

    Requests recommends a timeout be set in all production use of request sessions. This adapter adds a timeout by
    default but allows for overriding if desired.
    """

    @property
    def default_timeout(self) -> float:
        return float(getattr(self, "_default_timeout", REQUESTS_TIMEOUT))

    @default_timeout.setter
    def default_timeout(self, value: Union[int, float]) -> None:
        self._default_timeout = float(value)

    def send(
        self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None
    ):
        # Apply the default timeout if one was not manually passed
        if timeout is None:
            timeout = self.default_timeout
        return super().send(
            request,
            stream=stream,
            timeout=timeout,
            verify=verify,
            cert=cert,
            proxies=proxies,
        )
