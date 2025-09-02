from typing import Callable, Any, Optional
from atatus.base import get_client
from atatus.instrumentation.packages.base import AbstractInstrumentedModule
from atatus.utils.logging import get_logger

logger = get_logger("atatus")

class OtelTracerInstrumentation(AbstractInstrumentedModule):
    name = "opentelemetry-tracer"
    atatus_get_tracer: Optional[Callable[..., Any]]
    instrument_list = ()

    try:
        from atatus.contrib.opentelemetry.trace import get_tracer
        atatus_get_tracer = get_tracer
        instrument_list = (("opentelemetry.trace", "get_tracer"),)
    except ImportError:
        logger.debug("OpenTelemetry not installed, skipping OtelTracerInstrumentation.")
        atatus_get_tracer = None

    creates_transactions = True

    def call(self, module, method, wrapped, instance, args, kwargs):
        if self.atatus_get_tracer is None:
            return wrapped(*args, **kwargs)
        kwargs['atatus_client'] = get_client()
        return self.atatus_get_tracer(*args, **kwargs)
