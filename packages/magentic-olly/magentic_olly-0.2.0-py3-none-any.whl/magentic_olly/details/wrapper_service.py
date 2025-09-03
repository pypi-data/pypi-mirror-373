import logging
from typing import Optional
from opentelemetry import propagate, trace
from opentelemetry.trace import SpanKind, StatusCode, Status

from .wrapper_params import MagenticWrapperServiceParams
from .utils import constants, magentic_logger
from .utils.spans import SpansUtils
from .initializer import InitializerProvider
from .model import settings, ResourceType

class MagenticWrapperService:
    
    def __init__(self, params: MagenticWrapperServiceParams):
        self._params:MagenticWrapperServiceParams = params
        self._current_otel_context = self._params.otel_context
        self._client_handler = _ClientHandler(self._params)
        self._tracing_initializer = InitializerProvider.get_tracing_initializer()
        self._logging_initializer = InitializerProvider.get_logging_initializer()
        self._wrapped_function = None
        
    def run_lambda_handler(self, func, *args, **kwargs):
        response = None
        try:
            self._wrapped_function = func
            response = self._run_lambda_handler(func, *args, **kwargs)
        except _LambdaRunException as e:
            self._client_handler.end_spans(response)
            raise e.lambda_exception
        except Exception as e:
            magentic_logger.exception(f"Wrapper service error: {e}")
            response = self._execute_lambda(func, args, kwargs)
        return response
        
    def _run_lambda_handler(self, func, *args, **kwargs):
        magentic_logger.debug("Running magentic lambda handler.")
        self._perform_pre_processing()
        
        response = None
        with self._create_service_span_context_manager(self._create_span_name(func)) as service_span:
            response = self._execute_lambda(func, args, kwargs)
            func_path = self._extract_func_path(func)
            func_path = func_path.replace('.', '/')
            service_span.set_attribute("magentic.function.path", func_path)
            self._set_span_attributes(service_span, response)
            self._inject_tracing_context(response)
            
        response = self._perform_post_processing(response)
        magentic_logger.debug("Magentic lambda handler execution completed.")
        return response

    def _create_span_name(self, func):
        if not hasattr(func, '__name__'):
            return 'handler'
        return func.__name__
    
    def _extract_func_path(self, func):
        if not hasattr(func, '__name__'):
            return 'handler'
        if not hasattr(func, '__module__'):
            return func.__name__
        path = f"{func.__module__}.{func.__name__}"
        
        return path

    def _execute_lambda(self, func, args, kwargs):
        try:
            response = func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger(self._tracing_initializer.logger_name)
            logger.exception(f"Error occurred while executing magenticly wrapped lambda: {e}")
            raise _LambdaRunException(e)
        return response
            

    def _perform_pre_processing(self):
        magentic_logger.debug("Performing pre-processing for magentic wrapper service.")
        self._client_handler.handle_spans()
        self._create_current_service_resource()
        self._current_otel_context = self._client_handler.get_context()
        magentic_logger.debug("Pre-processing completed. Current OpenTelemetry context set.")
        
    
    def _perform_post_processing(self, response):
        magentic_logger.debug("Performing post-processing for magentic wrapper service.")
        self._client_handler.end_spans(response)
        self._tracing_initializer.force_flush()
        if self._logging_initializer:
            self._logging_initializer.force_flush()
        magentic_logger.debug("Post-processing completed. OpenTelemetry spans flushed.")
        return response
    
    def _set_span_attributes(self, service_span, response):
        if not self._params.is_app_sync_event:
            SpansUtils.set_span_magentic_attributes(service_span, self._params)
        SpansUtils.set_span_response_attributes(service_span, response)

    def _set_span_magentic_attributes(self, span):
        if not self._params.has_magentic_span_attrs:
            return
        attrs = self._params.magentic_span_attrs
        for key, value in attrs.items():
            self._set_span_attribute(span, key, value)
    
    def _set_span_attribute(self, span, key, value):
        if not span or not key:
            return
        if value is None or isinstance(value, (dict, list, tuple)):
            return
        span.set_attribute(key, str(value))

    def _create_current_service_resource(self):
        if self._params.is_state_machine_event:
            state_machine_name = self._params.state_machine_name
            self._tracing_initializer.set_service_resource(state_machine_name)
            self._extend_service_resource_attrs(state_machine_name)
        else:
            self._tracing_initializer.reset_service_resource()
            self._extend_service_resource_attrs()
    

    def _create_service_span_context_manager(self, func_name):
        service_tracer = self._get_tracer()
        span_manager = service_tracer.start_as_current_span(func_name,
                            context=self._current_otel_context,
                            kind=self._params.service_span_kind)
        return span_manager
    
    def _extend_service_resource_attrs(self, service_name: Optional[str] = None):
        resource_attributes = {}
        if self._params.has_instance_id:
            resource_attributes["server.instance.id"] = self._params.instance_id
        if self._params.arn:
            resource_attributes["resource.arn"] = self._params.arn
        resource_attributes["resource.platform"] = "AWS"
        resource_attributes["resource.type"] = self._select_server_type()
        if self._params.account_id:
            resource_attributes["aws.account.id"] = self._params.account_id
        if self._params.region:
            resource_attributes["aws.account.region"] = self._params.region
        if self._params.has_instance_id:
            resource_attributes["server.instance.id"] = str(self._params.instance_id)
        if self._params.is_state_machine_event:
            resource_attributes[constants.STATE_MACHINE_NAME_KEY] = self._params.state_machine_name
        if self._wrapped_function:
            func_path = self._extract_func_path(self._wrapped_function)
            resource_attributes["repo.relative.path"] = func_path
            if hasattr(self._wrapped_function, '__module__'):
                last_module = self._wrapped_function.__module__.split('.')[-1]
                resource_attributes["repo.module.name"] = last_module
        self._tracing_initializer.create_service_resource_with_attrs(resource_attributes, service_name)

    def _select_server_type(self):
        return ResourceType.STATE_MACHINE.value if self._params.is_state_machine_event else ResourceType.LAMBDA.value
    

    def _inject_tracing_context(self, response:dict[str, any]):
        if not self._tracing_initializer.propagate_context:
            return
        response.update(self._params.propagation_tracing_context)
        propagator = propagate.get_global_textmap()
        otel_context = {}
        propagator.inject(otel_context)
        response[constants.OTEL_TRACE_CONTEXT_KEY] = otel_context
    
    def _get_tracer(self):
        if self._wrapped_function:
            func_path = self._extract_func_path(self._wrapped_function)
            return trace.get_tracer(func_path)
        return trace.get_tracer(__name__)



class _ClientHandler:
    def __init__(self, params: MagenticWrapperServiceParams):
        self._params = params
        self._spans = []
        self._tracing_initializer = InitializerProvider.get_tracing_initializer()
        self._client_service_name = params.client_service_name
        self._current_otel_context = self._params.otel_context
    
    
    def handle_spans(self):
        if self._client_service_name is None:
            return
        self._switch_to_client_resource()
        retro_server_span = self._create_retro_server_span()
        retro_client_span = self._create_retro_client_span()
        if retro_server_span:
            self._spans.append(retro_server_span)
        if retro_client_span:
            self._spans.append(retro_client_span)
            
    def get_context(self):
        return self._current_otel_context
    
    def end_spans(self, response:dict[str, any]):
        for span in reversed(self._spans):
            SpansUtils.set_span_magentic_attributes(span, self._params)
            SpansUtils.set_span_response_attributes(span, response)
            span.end()
        self._spans.clear()
            
    def _switch_to_client_resource(self):
        service_name = self._params.client_service_name
        resource_attributes = {}
        resource_attributes["resource.platform"] = "AWS"
        resource_attributes["resource.type"] = self._params.client_service_type
        if self._params.client_service_arn: 
            resource_attributes["resource.arn"] = self._params.client_service_arn
        self._tracing_initializer.create_service_resource_with_attrs(resource_attributes, service_name)
        
    def _create_retro_server_span(self):
        if not self._params.should_create_retro_server_span:
            return None  
        service_tracer = self._get_tracer()
        span = service_tracer.start_span("retro-server-span", 
                                                  context=self._current_otel_context, 
                                                  kind=SpanKind.SERVER)
        for key, value in self._params.proxy_attrs.items():
            span.set_attribute(key, value)
        self._current_otel_context = trace.set_span_in_context(span)
        return span

    def _get_tracer(self):
        return trace.get_tracer(__name__)

    def _create_retro_client_span(self):
        if self._client_service_name is None:
            return None
        client_tracer = self._get_tracer()
        span = client_tracer.start_span("retro-client-span",
                                                context=self._current_otel_context,
                                                kind=SpanKind.CLIENT)
        self._current_otel_context = trace.set_span_in_context(span)
        return span

class _LambdaRunException(Exception):
    def __init__(self, lambda_exception: Exception):
        super().__init__(lambda_exception)
        self.lambda_exception = lambda_exception