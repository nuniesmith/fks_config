"""
FKS Metrics Helper - Provides consistent Prometheus metrics across all services.

Usage:
    from fks_metrics import setup_metrics
    setup_metrics(app, service_name="fks_myservice", version="1.0.0")

This will:
    1. Register fks_build_info gauge
    2. Add /metrics endpoint
    3. Optionally add HTTP request metrics
"""
import os
import logging
from prometheus_client import CollectorRegistry, Gauge, Counter, Histogram, generate_latest, REGISTRY

logger = logging.getLogger(__name__)

# Shared registry for all FKS services
_fks_registry = CollectorRegistry()

# Build info gauge (registered once per process)
_build_info_registered = False


def get_fks_registry():
    """Get the shared FKS metrics registry."""
    return _fks_registry


def setup_metrics(
    app,
    service_name: str,
    version: str = "1.0.0",
    commit: str = None,
    build_date: str = None,
    enable_http_metrics: bool = False,
):
    """
    Set up Prometheus metrics for a FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service (e.g., "fks_ai")
        version: Service version
        commit: Git commit SHA (optional)
        build_date: Build timestamp (optional)
        enable_http_metrics: Whether to add HTTP request metrics
    """
    global _build_info_registered
    
    from fastapi.responses import PlainTextResponse
    
    # Create a registry for this service
    registry = CollectorRegistry()
    
    # Build info gauge - required for preflight validation
    build_info = Gauge(
        "fks_build_info",
        "Build information for the service",
        ["service", "version", "commit", "build_date"],
        registry=registry,
    )
    
    commit = commit or os.getenv("GIT_COMMIT", os.getenv("COMMIT_SHA", "unknown"))
    build_date = build_date or os.getenv("BUILD_DATE", os.getenv("BUILD_TIMESTAMP", "unknown"))
    
    build_info.labels(
        service=service_name,
        version=version,
        commit=commit,
        build_date=build_date,
    ).set(1)
    
    logger.info(f"✅ Registered fks_build_info for {service_name} v{version}")
    
    # HTTP metrics (optional)
    if enable_http_metrics:
        http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"],
            registry=registry,
        )
        http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"],
            registry=registry,
        )
        
        @app.middleware("http")
        async def metrics_middleware(request, call_next):
            import time
            start = time.time()
            response = await call_next(request)
            duration = time.time() - start
            
            endpoint = request.url.path
            method = request.method
            status = response.status_code
            
            http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
            http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
            
            return response
    
    # Add /metrics endpoint
    @app.get("/metrics", response_class=PlainTextResponse, include_in_schema=False)
    async def metrics_endpoint():
        return PlainTextResponse(
            generate_latest(registry).decode("utf-8"),
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    
    logger.info(f"✅ Metrics endpoint registered at /metrics for {service_name}")
    return registry


def setup_metrics_simple(
    service_name: str,
    version: str = "1.0.0",
):
    """
    Simple metrics setup for non-FastAPI services (returns registry).
    
    Returns:
        tuple: (registry, metrics_text_function)
    """
    registry = CollectorRegistry()
    
    build_info = Gauge(
        "fks_build_info",
        "Build information for the service",
        ["service", "version"],
        registry=registry,
    )
    build_info.labels(service=service_name, version=version).set(1)
    
    def get_metrics_text():
        return generate_latest(registry).decode("utf-8")
    
    return registry, get_metrics_text
