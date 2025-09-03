from typing import Optional

from opentelemetry import propagate, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import SpanKind, Status, StatusCode

from . import BaseInitializer
from ..exporter import filter_spans_exporter
from ..instrumentor import magentic_instrumentor
from ..model import model, settings
from ..utils import magentic_logger

class TracingInitializer(BaseInitializer):
    def __init__(self, params: model.InstrumentationParams):
        super().__init__(params)
        self._instrumentors = [
            magentic_instrumentor.MagenticInstrumentor()
        ]
        self._processor = self._create_processor()
        self._instrumentors.extend(params.extra_instrumentors)
        self._service_resource = self._create_resource()
        

    def initialize(self):
        self._create_tracer_provider()
        self._instrument_external_libs()
    
    def create_service_resource_with_attrs(self, attributes: dict, service_name: Optional[str] = None):
        attributes['service.name'] = service_name or self._params.service_name
        module_name = attributes.get('repo.module.name', None)
        if (not service_name) and module_name:
            attributes['service.name'] = f"{self._params.service_name}:{module_name}"
        attributes['service.environment'] = self._params.system_environment or "Unknown"
        filtered_attrs = {k: v for k, v in attributes.items() if v is not None and not isinstance(v, (dict, list, tuple))}
        self._service_resource = Resource.create(filtered_attrs)
        self._create_tracer_provider()
        self._instrument_external_libs()
        
    def set_service_resource(self, service_name: Optional[str] = None):
        resource = self._create_resource(service_name)
        self._create_tracer_provider(resource)
        
    def reset_service_resource(self):
        self._create_tracer_provider()
            
    def force_flush(self):
        magentic_logger.info("Forcing flush of tracing spans.")
        ret = self._processor.force_flush()
        magentic_logger.info(f"Tracing spans flushed with result: {ret}")
        return ret

    @property
    def service_name(self):
        return self._params.service_name
    
    @property
    def logger_name(self):
        return f"{self._params.service_name}-{self._params.system_environment}"
    
    @property
    def propagate_context(self):
        return self._params.propagate_context

    def _create_tracer_provider(self, resource:Optional[Resource]=None):
        tracer_provider = TracerProvider(resource=resource or self._service_resource)
        tracer_provider.add_span_processor(self._processor)
        trace._TRACER_PROVIDER = tracer_provider


    def _create_processor(self):
        exporter = self._create_exporter()
        processor = BatchSpanProcessor(exporter, max_export_batch_size=5, 
                                       schedule_delay_millis=10000,
                                       export_timeout_millis=settings.magentic_tracing_export_timeout)                
        return processor

    def _create_exporter(self):
        exporters = {
            model.ExportMode.CONSOLE: ConsoleSpanExporter(),
            model.ExportMode.HTTP: filter_spans_exporter.HttpFilterExporter(
                endpoint=f"{self._params.export_server_url}/v1/traces",
                headers={"Authorization": f"Bearer {self._params.export_server_token}"}
            ),
            model.ExportMode.GRPC: filter_spans_exporter.GrpcFilterExporter(
                endpoint=f"{self._params.export_server_url}"
            )
        }
        export_mode = self._get_export_mode()
        magentic_logger.debug("Using export mode: %s", export_mode)
        return exporters.get(export_mode, ConsoleSpanExporter())

    def _get_export_mode(self):
        export_options = {
            1: model.ExportMode.CONSOLE,
            2: model.ExportMode.HTTP,
            3: model.ExportMode.GRPC
        }
        return export_options.get(settings.magentic_tracing_export_mode, self._params.export_mode)

    def _instrument_external_libs(self):
        magentic_logger.debug("Instrumenting external libraries with OpenTelemetry.")
        for instrumentor in self._instrumentors:
            if instrumentor.is_instrumented_by_opentelemetry:
                instrumentor.uninstrument()
            instrumentor.instrument()
        magentic_logger.debug("External libraries instrumented with OpenTelemetry.")
