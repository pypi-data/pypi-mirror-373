import os

from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Iterator, Mapping, Optional, Set, cast

from fastapi import FastAPI, Request, Response, status
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Host, Mount
from starlette.types import ASGIApp, Lifespan

from .instrumentation import instrument
from .middleware import RequestHTTPLogger, SetRootPathMiddleware


DEFAULT_API_HOSTNAME = (
    "127.0.0.2"  # For local development, if $CLUSTER_API_DOMAIN is not set
)


class App(FastAPI):
    def setup(self) -> None:
        if not self.swagger_ui_init_oauth:
            self.swagger_ui_init_oauth = {"clientId": "delphai-api"}

        super().setup()

        self.add_middleware(SetRootPathMiddleware)
        self.add_event_handler("startup", self._include_dependency_responses)

        try:
            import httpx
        except ImportError:
            pass
        else:
            self.add_exception_handler(httpx.TimeoutException, self._timeout_error)

        instrument(self, self.extra.get("instrumentator_options"))

    def with_public_api(self, public_api_app: FastAPI) -> ASGIApp:
        """
        Combines `self` and gived application into new ASGI app with domain-based routing
        "$CLUSTER_API_DOMAIN" host is served by `public_api_app`, the rest by this app
        """
        api_hostname = os.environ.get("CLUSTER_API_DOMAIN", DEFAULT_API_HOSTNAME)

        public_api_app.extra["oidc_audience"] = "public-api"
        public_api_app.extra["metrics_handler_prefix"] = f"//{api_hostname}"

        api_logger_endpoint = os.environ.get("API_LOGGER_ENDPOINT")
        if api_logger_endpoint:
            public_api_app.add_middleware(
                RequestHTTPLogger,
                logger_endpoint=api_logger_endpoint,
            )

        return Starlette(
            routes=[
                Host(api_hostname, public_api_app),
                Mount("", self),
            ],
            lifespan=self._merge_lifespan_contexts(
                public_api_app.router.lifespan_context
            ),
        )

    # based on fastapi.routing:
    def _merge_lifespan_contexts(self, nested_context: Lifespan[Any]) -> Lifespan[Any]:
        @asynccontextmanager
        async def merged_lifespan(
            app: FastAPI,
        ) -> AsyncIterator[Optional[Mapping[str, Any]]]:
            async with self.router.lifespan_context(app) as maybe_original_state:
                async with nested_context(app) as maybe_nested_state:
                    if maybe_nested_state is None and maybe_original_state is None:
                        yield None  # old ASGI compatibility
                    else:
                        yield {
                            **(maybe_nested_state or {}),
                            **(maybe_original_state or {}),
                        }

        return cast(Lifespan[Any], merged_lifespan)

    def _include_dependency_responses(self) -> None:
        for route in self.routes:
            if isinstance(route, APIRoute):
                for dependency in self._walk_dependency_tree(route.dependant):
                    dependency_responses = getattr(dependency.call, "responses", None)
                    if dependency_responses:
                        route.responses = dict(dependency_responses, **route.responses)

                endpoint_responses = getattr(route.endpoint, "responses", None)
                if endpoint_responses:
                    route.responses = dict(endpoint_responses, **route.responses)

    def _walk_dependency_tree(
        self, dependant: Dependant, visited: Optional[Set[Any]] = None
    ) -> Iterator[Dependant]:
        if visited is None:
            visited = set()
        visited.add(dependant.cache_key)

        for sub_dependant in dependant.dependencies:
            if sub_dependant.cache_key in visited:
                continue

            yield sub_dependant
            yield from self._walk_dependency_tree(sub_dependant, visited)

    def _timeout_error(self, request: Request, error: Exception) -> Response:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"detail": "Gateway Timeout"},
        )
