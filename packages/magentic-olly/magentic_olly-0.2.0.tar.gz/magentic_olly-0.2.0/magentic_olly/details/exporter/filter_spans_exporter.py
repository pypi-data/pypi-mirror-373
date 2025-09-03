from opentelemetry.trace import SpanKind
from opentelemetry.sdk.trace.export import SpanExportResult
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as HttpSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as GrpcSpanExporter
from ..utils import magentic_logger

class _FilterSpansMixin:
    def export(self, spans) -> SpanExportResult:
        try:
            return self._export_traces(spans)
        except Exception as e:
            magentic_logger.exception(f"Error exporting traces: {e}")
        return SpanExportResult.FAILURE

    def _export_traces(self, spans) -> SpanExportResult:
        filtered_spans = [
            span for span in spans
            if not (span.name == "EventBridge.PutEvents" and span.kind == SpanKind.CLIENT)
        ]
        if filtered_spans:
            return super().export(filtered_spans)
        return SpanExportResult.SUCCESS

class HttpFilterExporter(_FilterSpansMixin, HttpSpanExporter):
    pass

class GrpcFilterExporter(_FilterSpansMixin, GrpcSpanExporter):
    pass
