# logzai.py
import atexit
import logging
from typing import Optional
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

_logger: Optional[logging.Logger] = None
_provider: Optional[LoggerProvider] = None

def init(
    ingest_token: str,
    ingest_endpoint: str = "http://ingest.logz.ai",
    min_level: int = logging.DEBUG,
    *,
    service_name: str = "app",
    service_namespace: str = "app-home",
    environment: str = "prod",
    protocol: str = "http",  # "http" | "grpc"
) -> None:
    """Initialize the global LogzAI logger."""
    global _logger, _provider

    resource = Resource.create({
        "ingest_token": ingest_token,
        "service.name": service_name,
        "service.namespace": service_namespace,
        "deployment.environment": environment,
    })

    _provider = LoggerProvider(resource=resource)

    if protocol.lower() == "grpc":
        from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
        exporter = OTLPLogExporter(endpoint=ingest_endpoint)
    else:
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        exporter = OTLPLogExporter(
            endpoint=ingest_endpoint,
            headers=(("x_ingest_token", ingest_token),),
        )

    _provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

    handler = LoggingHandler(level=logging.NOTSET, logger_provider=_provider)
    _logger = logging.getLogger("logzai")
    _logger.setLevel(min_level)  # let caller decide level per message
    _logger.addHandler(handler)
    _logger.propagate = False

    atexit.register(shutdown)

def log(level: int, message: str, *, stacklevel: int = 2, **kwargs) -> None:
    """Send a log with an explicit level. Extra kwargs become structured attributes.

    stacklevel controls which frame is reported as the caller. Default (2) points to the
    user's frame when calling this function directly. Wrappers add +1 per extra layer.
    """
    if not _logger:
        raise RuntimeError("LogzAI not initialized. Call logzai.init(...) first.")
    _logger.log(level, message, extra=kwargs, stacklevel=stacklevel)

# --- Convenience wrappers ---
def debug(message: str, **kwargs) -> None:
    log(logging.DEBUG, message, stacklevel=3, **kwargs)

def info(message: str, **kwargs) -> None:
    log(logging.INFO, message, stacklevel=3, **kwargs)

def warning(message: str, **kwargs) -> None:
    log(logging.WARNING, message, stacklevel=3, **kwargs)

def warn(message: str, **kwargs) -> None:  # alias
    # Align stacklevel with other convenience wrappers
    log(logging.WARNING, message, stacklevel=3, **kwargs)

def error(message: str, **kwargs) -> None:
    log(logging.ERROR, message, stacklevel=3, **kwargs)

def critical(message: str, **kwargs) -> None:
    log(logging.CRITICAL, message, stacklevel=3, **kwargs)

def shutdown() -> None:
    """Flush and shutdown the logger provider."""
    global _provider
    if _provider:
        try:
            _provider.shutdown()
        except Exception:
            pass
        _provider = None
