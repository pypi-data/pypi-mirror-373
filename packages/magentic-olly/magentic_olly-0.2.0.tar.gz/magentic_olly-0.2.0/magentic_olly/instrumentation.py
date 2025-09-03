import sys
from functools import wraps
from typing import Optional
import logging

_original_warning_fcn = logging.Logger.warning

def _warning_fcn(self, msg, *args, **kwargs):
        blackluist = ["force_flush", "Exporter already shutdown"]
        if any(kw in msg for kw in blackluist):
            # Skip logging this message if it contains 'force_flush'
            return
        return _original_warning_fcn(self, msg, *args, **kwargs)
    
logging.Logger.warning = _warning_fcn
logging.Logger.warn = _warning_fcn

from .details.model import model
from .details import wrapper_service, initializer, settings, magentic_logger
from .details.utils import utils

def magentic_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not settings.magentic_instrumentation_enabled:
            magentic_logger.warning("Magentic instrumentation is disabled. Skipping wrapper.")
            return func(*args, **kwargs)
        
        event, context = utils.Utils.extract_event_and_context(args, kwargs)

        service_params = wrapper_service.MagenticWrapperServiceParams(
            event=event,
            lambda_context=context
        )
        
        magentic_service = wrapper_service.MagenticWrapperService(service_params)
        response = magentic_service.run_lambda_handler(func, *args, **kwargs)
        return response

    
    
    return wrapper

def initialize(params: Optional[model.InstrumentationParams]=None):
    if params is None:
        params = model.InstrumentationParams()
    magentic_logger.info(f"Settings: {settings}")
    magentic_logger.info(f"Params: {params}")
    if not settings.magentic_instrumentation_enabled:
        magentic_logger.warning("Magentic instrumentation is disabled. Skipping initialization.")
        return
    
    if settings.magentic_tracing_enabled:
        tracing_initializer = initializer.InitializerProvider.create_tracing_initializer(params)
        tracing_initializer.initialize()
        magentic_logger.info("OpenTelemetry tracing initialized.")
        
    if settings.magentic_logging_enabled and not _is_pytest():
        logging_initializer = initializer.InitializerProvider.create_logging_initializer(params)
        logging_initializer.initialize()
        magentic_logger.info("OpenTelemetry logging initialized.")

def _is_pytest():
    return "pytest" in sys.modules
