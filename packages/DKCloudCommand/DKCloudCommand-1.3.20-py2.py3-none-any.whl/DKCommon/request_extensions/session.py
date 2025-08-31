import logging
import time
from typing import Optional, Union

from requests import Session

from .settings import RATE_LIMIT_HEADERS, RETRIES
from .utils import parse_rate_limit

LOG = logging.getLogger(__name__)


class ExtendedSession(Session):
    @staticmethod
    def _has_retry_text(value: Optional[str]) -> bool:
        try:
            return "please try again in a bit" in value
        except (TypeError, ValueError):
            return False

    def request(
        self,
        method,
        url,
        params=None,
        data=None,
        headers=None,
        cookies=None,
        files=None,
        auth=None,
        timeout=None,
        allow_redirects=True,
        proxies=None,
        hooks=None,
        stream=None,
        verify=None,
        cert=None,
        json=None,
    ):
        """
        Dispatch requests with special handling for rate-limited auth endpoints.

        For 401 errors, sometimes rate-limiting is at play. If rate-limit headers are present, honor their
        wait times. For other endpoints response text is sometimes used to indicate rate limiting, in known
        cases, fallback to a retry strategy for the request.
        """
        kwargs = {
            "params": params,
            "data": data,
            "headers": headers,
            "cookies": cookies,
            "files": files,
            "auth": auth,
            "timeout": timeout,
            "allow_redirects": allow_redirects,
            "proxies": proxies,
            "hooks": hooks,
            "stream": stream,
            "verify": verify,
            "cert": cert,
            "json": json,
        }
        if method.upper() != "POST":
            return super().request(method, url, **kwargs)

        response = super().request(method, url, **kwargs)
        if response.status_code != 401:
            return response

        # If there were any rate-limit headers, parse them and wait the appropriate time then try again.
        response_headers = response.headers
        rate_gen = (response_headers.get(x) for x in RATE_LIMIT_HEADERS)
        rate_limit: Union[str, int, None] = next((x for x in rate_gen if x), None)

        if rate_limit:
            try:
                converted_rate_limit = float(rate_limit)
            except (ValueError, TypeError):
                LOG.warning("Ignored invalid rate limit value: `%s`", rate_limit)
                return response
            else:
                wait = parse_rate_limit(converted_rate_limit)
                LOG.debug("Sleeping for %s seconds to honor Rate-Limit headers", wait)
                time.sleep(wait)
                return super().request(method, url, **kwargs)

        if self._has_retry_text(response.text):
            for i in range(RETRIES):
                wait = 0.5 * (2 ** (i - 1))
                time.sleep(wait)
                LOG.debug("Sleeping for %s seconds to retry authentication.", wait)
                response = super().request(method, url, **kwargs)
                if response.status_code != 401:
                    return response
                else:
                    if self._has_retry_text(response.text):
                        continue
                    else:
                        return response
            else:
                return super().request(method, url, **kwargs)
        else:
            return super().request(method, url, **kwargs)
