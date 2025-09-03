from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter, LogExportResult

class FilterLogsExporter(OTLPLogExporter):
    def export(self, log_records):
        try:
            print("Exporting logs with FilterLogsExporter...")
            return self._export_logs(log_records)
        except Exception as e:
            print(f"Error exporting logs: {e}")
        return LogExportResult.FAILURE
    
    def _export_logs(self, log_records):
        filtered_log_records = []
        ignored_scopes = {"opentelemetry.attributes"}
        for record in log_records:
            if hasattr(record, "instrumentation_scope") and getattr(record.instrumentation_scope, "name", None) in ignored_scopes:
                continue
            filtered_log_records.append(record)

        return super().export(filtered_log_records)
    
    
