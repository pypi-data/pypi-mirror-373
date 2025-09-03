from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, Gauge, generate_latest
from prometheus_fastapi_instrumentator import metrics
from prometheus_fastapi_instrumentator.middleware import (
    PrometheusInstrumentatorMiddleware,
)
from starlette.applications import Starlette
from typing import Any, Dict, Optional

from .authorization import Authorization


METRICS_URL = "/metrics"


DEFAULT_INSTRUMENTATIONS = [metrics.default()]


class PatchedPrometheusInstrumentatorMiddleware(PrometheusInstrumentatorMiddleware):
    """
    prometheus-fastapi-instrumentator==7.0.0 doesn't support
    instrumenting more than one application at once:

    Traceback (most recent call last):
      File "python-3.9.7/lib/python3.9/site-packages/prometheus_fastapi_instrumentator/middleware.py", line 115, in __init__
        self.inprogress = Gauge(
      File "python-3.9.7/lib/python3.9/site-packages/prometheus_client/metrics.py", line 399, in __init__
        super().__init__(
      File "python-3.9.7/lib/python3.9/site-packages/prometheus_client/metrics.py", line 156, in __init__
        registry.register(self)
      File "python-3.9.7/lib/python3.9/site-packages/prometheus_client/registry.py", line 43, in register
        raise ValueError(
    ValueError: Duplicated timeseries in CollectorRegistry: {'http_requests_inprogress'}

    This class instantiates singletons and reuses them for all middleware instances
    """

    INPROGRESS_GAUGE = Gauge(
        name="http_requests_inprogress",
        documentation="Number of HTTP requests in progress.",
        labelnames=("method", "handler"),
        multiprocess_mode="livesum",
    )

    def __init__(
        self,
        app: Starlette,
        *,
        should_instrument_requests_inprogress: bool = False,
        inprogress_labels: bool = True,
        inprogress_name: str = "http_requests_inprogress",
        **kwargs: Any,
    ):
        assert inprogress_labels, "Changing this parameter is not supported"
        assert (
            inprogress_name == "http_requests_inprogress"
        ), "Changing this parameter is not supported"

        super().__init__(
            app,
            should_instrument_requests_inprogress=False,
            inprogress_name=inprogress_name,
            inprogress_labels=inprogress_labels,
            **kwargs,
        )

        self.should_instrument_requests_inprogress = (
            should_instrument_requests_inprogress
        )
        if should_instrument_requests_inprogress:
            self.inprogress = self.INPROGRESS_GAUGE


def instrument(app: FastAPI, options: Optional[Dict]) -> None:
    if isinstance(options, bool) and not options:
        # Disabled when `options == False`
        return None

    options = {
        "should_group_status_codes": False,
        "excluded_handlers": [METRICS_URL],
        "should_instrument_requests_inprogress": True,
        "inprogress_labels": True,
        "instrumentations": [_add_handler_prefix] + DEFAULT_INSTRUMENTATIONS,
        **(options or {}),
    }

    app.add_middleware(
        PatchedPrometheusInstrumentatorMiddleware,
        **options,
    )

    @app.get(METRICS_URL, include_in_schema=False)
    def metrics(authorization: Authorization) -> Response:
        """Endpoint that serves Prometheus metrics."""

        authorization.require(authorization.is_direct_request)

        return Response(
            headers={"Content-Type": CONTENT_TYPE_LATEST},
            content=generate_latest(REGISTRY),
        )


def _add_handler_prefix(info: metrics.Info) -> None:
    metrics_handler_prefix = info.request.app.extra.get("metrics_handler_prefix")
    if metrics_handler_prefix:
        info.modified_handler = metrics_handler_prefix + info.modified_handler
