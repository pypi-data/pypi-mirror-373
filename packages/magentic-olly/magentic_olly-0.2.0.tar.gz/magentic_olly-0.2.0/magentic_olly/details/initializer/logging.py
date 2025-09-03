import logging

from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter, SimpleLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter as HttpLogExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter as GrpcLogExporter

from . import BaseInitializer
from ..model import model, settings
from ..instrumentor import LoggingInstrumentor
from ..exporter import FilterLogsExporter
from ..utils import magentic_logger

class LoggingInitializer(BaseInitializer):
    def __init__(self, params: model.InstrumentationParams):
        super().__init__(params)
        self._processor = BatchLogRecordProcessor(self._create_exporter(),
                                                  schedule_delay_millis=10000,
                                                  export_timeout_millis=settings.magentic_logging_export_timeout)
        self._instrumentor = LoggingInstrumentor()
    
    def initialize(self):
        self._create_logging_provider()
        if not self._instrumentor.is_instrumented_by_opentelemetry:
            self._instrumentor.instrument()

    def _create_logging_provider(self):
        resource = self._create_resource(self._params.service_name)
        logger_provider = LoggerProvider(resource=resource)
        logger_provider.add_log_record_processor(
            self._processor
        )
        set_logger_provider(logger_provider)
        
    def force_flush(self):
        magentic_logger.info("Forcing flush of logging records.")
        ret = self._processor.force_flush()
        magentic_logger.info(f"Flushed logging records with result: {ret}")
        return ret

    def _create_exporter(self):
        exporters = {
            model.ExportMode.CONSOLE: ConsoleLogExporter(),
            model.ExportMode.HTTP: HttpLogExporter(
                endpoint=f"{self._params.export_server_url}/v1/logs",
                headers={"Authorization": f"Bearer {self._params.export_server_token}"}
            ),
            model.ExportMode.GRPC: GrpcLogExporter(
                endpoint=f"{self._params.export_server_url}"
            )
        }
        export_mode = self._get_export_mode()
        magentic_logger.debug("Using export mode: %s", export_mode)
        return exporters.get(export_mode, ConsoleLogExporter())

    def _get_export_mode(self):
        export_options = {
            1: model.ExportMode.CONSOLE,
            2: model.ExportMode.HTTP,
            3: model.ExportMode.GRPC
        }
        return export_options.get(settings.magentic_logging_export_mode, self._params.export_mode)

