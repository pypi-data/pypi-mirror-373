from prometheus_client import CollectorRegistry, Counter, Histogram

registry = CollectorRegistry()

HTTP_REQUESTS_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "auth_type"],
    registry=registry,
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint", "method"],
    registry=registry,
)

REQUEST_SIZE = Histogram(
    "http_request_size_bytes", "Size of HTTP request bodies", ["method", "endpoint"]
)

RESPONSE_SIZE = Histogram(
    "http_response_size_bytes",
    "Size of HTTP responses",
    ["method", "endpoint"],
    registry=registry,
)
