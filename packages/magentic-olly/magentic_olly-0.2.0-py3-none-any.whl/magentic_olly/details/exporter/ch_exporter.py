import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..model import db_models
from datetime import datetime
from opentelemetry.sdk.trace import ReadableSpan
from typing import List
import time

class ClickhouseOtelExporter:
    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(db_url)
        # db_models.Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def shutdown(self) -> None:
        self.engine.dispose()

    def export(self, spans: List[ReadableSpan]) -> None:
        session = self.Session()
        db_span_models = []
        start_time = time.time()
        try:
            for span in spans:
                db_span = self._create_db_model(span)
                db_span_models.append(db_span)
            session.bulk_save_objects(db_span_models)  # Faster bulk insert
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            elapsed = time.time() - start_time
            print(f"Exported {len(spans)} spans in {elapsed:.4f} seconds")

    def _create_db_model(self, span: ReadableSpan):
        ctx = span.get_span_context()
        trace_id = format(ctx.trace_id, '032x') if ctx else None
        span_id = format(ctx.span_id, '016x') if ctx else None

        parent_span_id = format(span.parent.span_id, '016x') if span.parent and span.parent.span_id else None
        trace_state = str(ctx.trace_state) if ctx and ctx.trace_state else None

        name = span.name if span.name else None
        kind = span.kind if span.kind else None
        span_kind = str(kind.name.capitalize()) if kind and kind.name else None

        ts = span.start_time // 1000 if span.start_time else 0
        start_time = datetime.fromtimestamp(ts / 1e6) if ts else None
        duration = int(span.end_time - span.start_time) if span.end_time and span.start_time else None

        resource = span.resource if span.resource else None
        service_name = resource.attributes.get('service.name') if resource and resource.attributes and resource.attributes.get else None
        resource_attrs = {str(k): str(v[0] if isinstance(v, tuple) else v) for k, v in resource.attributes.items()} if resource and resource.attributes else None
        span_attributes = {str(k): str(v[0] if isinstance(v, tuple) else v) for k, v in span.attributes.items()} if span.attributes else None

        scope = span.instrumentation_scope if span.instrumentation_scope else None
        scope_name = scope.name if scope and scope.name else None
        scope_version = scope.version if scope and scope.version else None

        status = span.status if span.status else None
        status_code = str(status.status_code) if status and status.status_code else None
        status_message = status.description if status and status.description else None

        db_span = db_models.Span(
            Timestamp=str(start_time) if start_time else None,
            TraceId=trace_id,
            SpanId=span_id,
            ParentSpanId=parent_span_id,
            TraceState=trace_state,
            SpanName=name,
            SpanKind=span_kind,
            ServiceName=service_name,
            ResourceAttributes=str(resource_attrs) if resource_attrs else None,
            ScopeName=scope_name,
            ScopeVersion=scope_version,
            SpanAttributes=str(span_attributes) if span_attributes else None,
            Duration=duration,
            StatusCode=status_code,
            StatusMessage=status_message
        )
        return db_span
