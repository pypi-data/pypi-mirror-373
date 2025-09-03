import boto3
import json
from opentelemetry import trace, propagate
from opentelemetry.trace import SpanKind
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from ..utils import constants
from ..utils import magentic_logger

class EventBridgeInstrumentor(BaseInstrumentor):
    _original_boto3_client = boto3.client

    def instrumentation_dependencies(self):
        return []

    def _instrument(self, **kwargs):
        def patched_boto3_client(*args, **kwargs):
            client = EventBridgeInstrumentor._original_boto3_client(*args, **kwargs)
            if hasattr(client, "put_events"):
                emitter_patcher = _PutEventsPatcher()
                emitter_patcher.patch_put_events(client)
            return client
        boto3.client = patched_boto3_client
        
    def _uninstrument(self, **kwargs):
        boto3.client = self._original_boto3_client
        

class _PutEventsPatcher:
    def __init__(self):
        self._original_put_events = None
        
    def patch_put_events(self, client):
        self._original_put_events = client.put_events

        def patched_put_events(*args, **kwargs):
            response = self._perform_put_events(args, kwargs)
            return response

        client.put_events = patched_put_events

    def _perform_put_events(self, args, kwargs):
        with self._create_service_span_context_manager('put_events') as span:
            try:
                self._inject_context_in_entries(kwargs)
                self._set_span_attributes_with_first_entry(span, kwargs)
            except Exception as e:
                magentic_logger.exception("Error occurred in patched put_events:", e)
            response = self._original_put_events(*args, **kwargs)
        return response

    def _inject_context_in_entries(self, kwargs):
        entries = kwargs.get('Entries', [])
        for entry in entries:
            try:
                detail = json.loads(entry.get('Detail', '{}')) 
            except Exception:
                detail = {}
            detail.update(self._create_tracing_context(entry))
            entry['Detail'] = json.dumps(detail)
        kwargs['Entries'] = entries
        
    def _set_span_attributes_with_first_entry(self, span, kwargs):
        if not span:
            return
        entries = kwargs.get('Entries', [])
        if not entries:
            return
        entry = entries[0] 
        span.set_attribute(constants.SERVERLESS_SYSTEM_KEY, str(constants.EVENT_BRIDGE))
        span.set_attribute(constants.AWS_EVENT_BRIDGE_BUS_KEY, str(entry.get('EventBusName', 'default')))
        span.set_attribute(constants.AWS_EVENT_BRIDGE_SOURCE_KEY, str(entry.get('Source', 'default')))
        span.set_attribute(constants.AWS_EVENT_BRIDGE_DETAIL_TYPE_KEY, str(entry.get('DetailType', 'default')))


    def _create_service_span_context_manager(self, func_name):
        service_tracer = trace.get_tracer(__name__)
        span_manager = service_tracer.start_as_current_span(func_name, 
                            kind=SpanKind.PRODUCER)
        return span_manager

    def _create_tracing_context(self, entry) -> dict:
        attrs = {}
        propagator = propagate.get_global_textmap()
        otel_context = {}
        propagator.inject(otel_context)
        attrs[constants.SERVERLESS_SYSTEM_KEY] = constants.EVENT_BRIDGE
        attrs[constants.AWS_EVENT_BRIDGE_BUS_KEY] = entry.get('EventBusName', 'default')
        attrs[constants.AWS_EVENT_BRIDGE_SOURCE_KEY] = entry.get('Source', 'default')
        attrs[constants.AWS_EVENT_BRIDGE_DETAIL_TYPE_KEY] = entry.get('DetailType', 'default')
        
        context = {
            constants.MAGENTIC_SPAN_ATTRS: attrs,
            constants.OTEL_TRACE_CONTEXT_KEY: otel_context
        }
        return context
    
