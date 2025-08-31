"""
Type hints for the ExtendedSession instances that the request_extensions package provides. These are implemented as
parallel stubs rather than hints on the actual function signature because the function signature is so deeply nested
that the whole thing becomes quite unreadable and difficult to understand.
"""

from typing import IO, Any, Callable, Iterable, Mapping, MutableMapping, Text, Union

from _typeshed import SupportsItems
from requests import Session
from requests import auth as _auth
from requests import cookies, models
from requests.models import Response

RequestsCookieJar = cookies.RequestsCookieJar
Request = models.Request
PreparedRequest = models.PreparedRequest

_Data = (
    Text
    | bytes
    | Mapping[str, Any]
    | Mapping[Text, Any]
    | Iterable[tuple[Text, Text | None]]
    | IO[Any]
    | None
)

_Hook = Callable[[Response], Any]
_HooksInput = MutableMapping[Text, Iterable[_Hook] | _Hook]

_ParamsMappingKeyType = Text | bytes | int | float
_ParamsMappingValueType = (
    Text | bytes | int | float | Iterable[Text | bytes | int | float] | None
)
_Params = Union[
    SupportsItems[_ParamsMappingKeyType, _ParamsMappingValueType],
    tuple[_ParamsMappingKeyType, _ParamsMappingValueType],
    Iterable[tuple[_ParamsMappingKeyType, _ParamsMappingValueType]],
    Text | bytes,
]
_TextMapping = MutableMapping[Text, Text]

class ExtendedSession(Session):
    def request(
        self,
        method: str,
        url: str | bytes | Text,
        params: _Params | None = ...,
        data: _Data = ...,
        headers: _TextMapping | None = ...,
        cookies: None | RequestsCookieJar | _TextMapping = ...,
        files: MutableMapping[Text, IO[Any]]
        | MutableMapping[Text, tuple[Text, IO[Any]]]
        | MutableMapping[Text, tuple[Text, IO[Any], Text]]
        | MutableMapping[Text, tuple[Text, IO[Any], Text, _TextMapping]]
        | None = ...,
        auth: None
        | tuple[Text, Text]
        | _auth.AuthBase
        | Callable[[PreparedRequest], PreparedRequest] = ...,
        timeout: None | float | tuple[float, float] | tuple[float, None] = ...,
        allow_redirects: bool | None = ...,
        proxies: _TextMapping | None = ...,
        hooks: _HooksInput | None = ...,
        stream: bool | None = ...,
        verify: None | bool | Text = ...,
        cert: Text | tuple[Text, Text] | None = ...,
        json: Any | None = ...,
    ) -> Response: ...
