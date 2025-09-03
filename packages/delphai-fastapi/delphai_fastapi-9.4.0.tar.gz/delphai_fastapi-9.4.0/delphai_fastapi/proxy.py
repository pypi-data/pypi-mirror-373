import functools
import httpx
import logging
import re
import urllib.parse

from fastapi import Depends, Request
from httpx import USE_CLIENT_DEFAULT
from starlette.background import BackgroundTask
from starlette.datastructures import MutableHeaders
from starlette.responses import StreamingResponse
from typing import (
    List,
    Tuple,
    Annotated,
    Any,
    AsyncIterable,
    Callable,
    Iterable,
    Mapping,
    Optional,
    Union,
    cast,
)


logger = logging.getLogger(__file__)

httpx_client = httpx.AsyncClient(follow_redirects=True, timeout=60)


INTERNAL_HOSTNAMES = [
    "localhost",
    "svc",
    "svc.cluster.local",
]


async def _proxy_with_request(request: Request) -> Callable:
    return functools.partial(proxy_request, request)


Proxy = Annotated[Callable, Depends(_proxy_with_request)]

PrimitiveData = Optional[Union[str, int, float, bool]]

QueryParamTypes = Union[
    None, Mapping[str, PrimitiveData], List[Tuple[str, PrimitiveData]]
]


async def proxy_request(
    request: Request,
    url: str,
    *,
    method: Optional[str] = None,
    content: Union[None, str, bytes, Iterable[bytes], AsyncIterable[bytes]] = None,
    data: Optional[Mapping[str, Any]] = None,
    json: Optional[Any] = None,
    params: QueryParamTypes = None,
    headers: Optional[Mapping[str, Any]] = None,
    timeout: float = cast(float, USE_CLIENT_DEFAULT),
    follow_redirects: bool = cast(bool, USE_CLIENT_DEFAULT),
) -> StreamingResponse:
    if not params:
        params = cast(QueryParamTypes, request.query_params.multi_items())

    if headers:
        headers = MutableHeaders(headers)
    else:
        headers = request.headers.mutablecopy()

        try:
            del headers["Host"]
        except KeyError:
            pass

        if not _is_internal_call(url):
            try:
                del headers["Authorization"]
            except KeyError:
                pass

    if request.client:
        headers["X-Forwarded-For"] = ",".join(
            filter(None, [headers.get("X-Forwarded-For"), request.client.host])
        )

    if not content and not data and not json:
        content = request.stream()

    return await response_from_url(
        method=method or request.method,
        url=url,
        content=content,
        data=data,
        json=json,
        params=params,
        headers=headers,
        timeout=timeout,
        follow_redirects=follow_redirects,
    )


async def response_from_url(
    method: str,
    url: str,
    *,
    content: Union[None, str, bytes, Iterable[bytes], AsyncIterable[bytes]] = None,
    data: Optional[Mapping[str, Any]] = None,
    json: Optional[Any] = None,
    params: QueryParamTypes = None,
    headers: Optional[Mapping[str, Any]] = None,
    timeout: float = cast(float, USE_CLIENT_DEFAULT),
    follow_redirects: bool = cast(bool, USE_CLIENT_DEFAULT),
) -> StreamingResponse:
    request = httpx_client.build_request(
        method=method,
        url=url,
        content=content,
        data=data,
        json=json,
        params=params,
        headers=headers,
        timeout=timeout,
    )

    response = await httpx_client.send(
        request, stream=True, follow_redirects=follow_redirects
    )

    return StreamingResponse(
        content=response.aiter_raw(),
        status_code=response.status_code,
        headers=response.headers,
        background=BackgroundTask(response.aclose),  # `on_close` callback
    )


INTERNAL_HOSTNAMES_RE = [
    re.compile(r"(^|\.){}$".format(re.escape(hostname)))
    for hostname in INTERNAL_HOSTNAMES
]


def _is_internal_call(url: str) -> bool:
    hostname = urllib.parse.urlparse(url).hostname
    if not hostname:
        return False
    return any(regexp.search(hostname) for regexp in INTERNAL_HOSTNAMES_RE)
