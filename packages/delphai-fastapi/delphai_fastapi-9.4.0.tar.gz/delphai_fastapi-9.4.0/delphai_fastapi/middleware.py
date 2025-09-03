import asyncio
import httpx
import logging

from typing import Any, Callable

from fastapi import Request, Response
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from urllib.parse import urlsplit


logger = logging.getLogger(__file__)


class SetRootPathMiddleware(BaseHTTPMiddleware):
    """
    Set `root_path` to make proper URLs behind a proxy
    https://fastapi.tiangolo.com/advanced/behind-a-proxy/
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        original_url = request.headers.get("x-envoy-original-path")
        path = request.url.path

        if original_url:
            original_path = urlsplit(original_url).path

            if original_path.endswith(path):
                request.scope["root_path"] = original_path.removesuffix(path)

        return await call_next(request)


class RequestHTTPLogger(BaseHTTPMiddleware):
    """
    HTTP POST's metadata about each request handled
    """

    def __init__(self, app: ASGIApp, logger_endpoint: str) -> None:
        super().__init__(app=app)

        self.logger_endpoint = logger_endpoint
        self.http_client = httpx.AsyncClient()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        route = request.scope.get("route")

        coroutine = self.log_call(
            {
                "isApiCall": bool(route and isinstance(route, APIRoute)),
                "method": request.method,
                "url": str(request.url),
                "requestHeaders": request.headers.items(),
                "statusCode": response.status_code,
                "responseHeaders": response.headers.items(),
            }
        )
        asyncio.create_task(coroutine).add_done_callback(lambda future: future.result())

        return response

    async def log_call(self, json: Any) -> None:
        try:
            response = await self.http_client.post(self.logger_endpoint, json=json)
            response.raise_for_status()
        except Exception as error:
            logger.warning("Request logging failed: %s", repr(error))
