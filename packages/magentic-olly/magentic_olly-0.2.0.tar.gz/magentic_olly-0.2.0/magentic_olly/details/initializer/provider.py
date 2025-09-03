from . import TracingInitializer, LoggingInitializer
from ..utils import magentic_logger
from ..model import model

class InitializerProvider:
    _tracing_initializer = None
    _logging_initializer = None 
    @classmethod
    def create_tracing_initializer(cls, params: model.InstrumentationParams):
        cls._tracing_initializer = TracingInitializer(params)
        magentic_logger.debug("Creating tracing initializer with params: %s", params)
        return cls._tracing_initializer

    @classmethod
    def get_tracing_initializer(cls) -> TracingInitializer:
        magentic_logger.debug("Getting tracing initializer.")
        return cls._tracing_initializer
    
    @classmethod
    def create_logging_initializer(cls, params: model.InstrumentationParams):
        cls._logging_initializer = LoggingInitializer(params)
        magentic_logger.debug("Creating logging initializer with params: %s", params)
        return cls._logging_initializer
    
    @classmethod
    def get_logging_initializer(cls) -> LoggingInitializer:
        magentic_logger.debug("Getting logging initializer.")
        return cls._logging_initializer
    
    
