import os
from typing import Dict, Optional

from opentelemetry import propagate
from opentelemetry.trace import SpanKind
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from .instrumentor import magentic_instrumentor

from .utils import constants, magentic_logger
from .initializer import InitializerProvider
from .model import ResourceType

class MagenticWrapperServiceParams:
    def __init__(self, event: Optional[dict] = None,
                 lambda_context: Optional[object] = None):
        self._tracing_initializer = InitializerProvider.get_tracing_initializer()
        self._is_state_machine_event = False
        self._is_event_bridge_event = False
        self._main_event_data = None
        self.event = event
        self.lambda_context = lambda_context
        self.arn = hasattr(lambda_context, 'invoked_function_arn') and lambda_context.invoked_function_arn or None
        self.account_id = self._extract_account_id_from_arn(self.arn)
        self.region = self._extract_region_from_arn(self.arn)
        self._init()
        self.carrier:dict[str, str] = self._create_carrier()
        magentic_logger.debug(f"Carrier created: {self.carrier}")
        self.payload:dict[str, str] = self._create_payload()
        
        
    
    @property
    def otel_context(self):
        propagator = propagate.get_global_textmap()
        return propagator.extract(self.carrier)
    
    @property
    def client_service_name(self):
        if self.is_proxy_event:
            headers = self.headers
            return headers.get('host', None)
        if not self.has_magentic_span_attrs:
            return None
        return self.magentic_span_attrs.get(constants.CLIENT_NAME_KEY, None)
    
    @property
    def proxy_attrs(self):
        if not self.is_proxy_event:
            return {}
        request_context = self.event.get('requestContext', {})
        keys = ['httpMethod', 'resourcePath']
        return {f'proxy.{key.lower()}': request_context.get(key, None) for key in keys if request_context.get(key, None) is not None}
    
    @property
    def has_client_service_name(self):
        return self.client_service_name is not None
    
    @property
    def client_service_arn(self):
        if not self.has_magentic_span_attrs:
            return None
        return self.magentic_span_attrs.get(constants.CLIENT_ARN_KEY, None)
    
    @property
    def should_create_retro_server_span(self):
        return any([self.is_app_sync_event, self.is_proxy_event])

    @property
    def instance_id(self):
        if self.lambda_context and hasattr(self.lambda_context, 'aws_request_id'):
            return self.lambda_context.aws_request_id
        return None
    
    @property
    def has_instance_id(self):
        return self.instance_id is not None

    @property
    def is_state_machine_event(self):
        return self._is_state_machine_event

    @property
    def is_event_bridge_event(self):
        return self._is_event_bridge_event
    
    @property
    def is_app_sync_event(self):
        return constants.AWS_APP_SYNC_API_NAME in self.magentic_span_attrs
    
    @property
    def client_service_arn(self):
        if not self.has_magentic_span_attrs:
            return None
        return self.magentic_span_attrs.get(constants.CLIENT_ARN_KEY, None)
    
    @property
    def state_machine_name(self):
        if not self.is_state_machine_event:
            return None
        return self.magentic_span_attrs.get(constants.STATE_MACHINE_NAME_KEY, None)

    @property
    def main_event_data(self):
        return self._main_event_data
    
    @property
    def client_service_type(self):
        if self.is_proxy_event:
            return ResourceType.PROXY.value
        if self.is_event_bridge_event:
            return ResourceType.EVENT_BRIDGE.value
        if self.is_state_machine_event:
            return ResourceType.STATE_MACHINE.value
        if self.is_app_sync_event:
            return ResourceType.APP_SYNC.value
        
        return ResourceType.LAMBDA.value
    

    
    def _init(self):
        self._main_event_data = self.event
        self._is_state_machine_event = (constants.STATE_MACHINE == self._get_serverless_system(self._main_event_data))
        if self._is_state_machine_event:
            self._main_event_data = self._main_event_data.get(constants.STATE_MACHINE_ORIGINAL_PAYLOAD_KEY, {})
            
        if self._is_event_bridge_event_schema():
            details = self._get_details()
            serverless_system = self._get_serverless_system(details)
            self._is_event_bridge_event = (constants.EVENT_BRIDGE == serverless_system) if serverless_system is not None else True
        

    def _get_details(self):
        main_event_keys = ['Detail', 'detail']
        details = self._get_first_value(main_event_keys)
        return details

    def _is_event_bridge_event_schema(self):
        schema_keys = ['version', 'id', 'detail-type', 'source', 'account', 'time', 'region', 'resources']
        return all(key in self.main_event_data for key in schema_keys)

    @staticmethod
    def _get_serverless_system(event):
        return event.get(constants.MAGENTIC_SPAN_ATTRS, {}).get(constants.SERVERLESS_SYSTEM_KEY, None)

    def _get_first_value(self, keys):
        for key in keys:
            if key in self.main_event_data:
                return self.main_event_data[key]
        return None

    @property
    def service_span_kind(self):
        if self.is_event_bridge_event:
            magentic_logger.debug("Detected EventBridge event, setting span kind to CON")
            return SpanKind.CONSUMER
        magentic_logger.debug("Detected non-EventBridge event, setting span kind to SERVER")
        return SpanKind.SERVER
    
    @property
    def magentic_span_attrs(self) -> dict:
        attrs = self.main_event_data.get(constants.MAGENTIC_SPAN_ATTRS, {})
        if self.is_state_machine_event:
            attrs.update(self.event.get(constants.MAGENTIC_SPAN_ATTRS, {}))
        if not self.is_event_bridge_event:
            return attrs
        self._add_event_bridge_attrs(attrs)
        attrs.update(self._get_details().get(constants.MAGENTIC_SPAN_ATTRS, {}))
        return attrs
    
    @property
    def is_proxy_event(self):
        headers = self.headers
        if not headers:
            return False
        proxy_keys = ['x-forwarded-for']
        return any(key in headers for key in proxy_keys)

    def _add_event_bridge_attrs(self, attrs):
        attrs[constants.SERVERLESS_SYSTEM_KEY] = constants.EVENT_BRIDGE
        event_bridge_bus = self._get_details().get(constants.MAGENTIC_SPAN_ATTRS, {}).get(constants.AWS_EVENT_BRIDGE_BUS_KEY, None)
        account_id = self._get_first_value(['Account', 'account'])
        region = self._get_first_value(['Region', 'region'])
        bus_arn = f'arn:aws:events:{region}:{account_id}:event-bus/{event_bridge_bus}' if account_id and region and event_bridge_bus else None
        if event_bridge_bus:
            attrs[constants.AWS_EVENT_BRIDGE_BUS_KEY] = event_bridge_bus
        if bus_arn:
            attrs[constants.AWS_EVENT_BRIDGE_BUS_ARN] = bus_arn
        event_bridge_source = self._get_first_value(['Source', 'source'])
        if event_bridge_source:
            attrs[constants.AWS_EVENT_BRIDGE_SOURCE_KEY] = event_bridge_source
        event_bridge_detail_type = self._get_first_value(['DetailType', 'detail-type'])
        if event_bridge_detail_type:
            attrs[constants.AWS_EVENT_BRIDGE_DETAIL_TYPE_KEY] = event_bridge_detail_type
        

    @property
    def has_magentic_span_attrs(self):
        return (constants.MAGENTIC_SPAN_ATTRS in self.main_event_data) or self.is_event_bridge_event

    @property
    def propagation_tracing_context(self) -> dict:
        tracing_context = {}
        tracing_context[constants.MAGENTIC_SPAN_ATTRS] = {}
        for key, value in self.magentic_span_attrs.items():
            if key not in constants.IGNORE_PROPAGATION_KEYS:
                tracing_context[constants.MAGENTIC_SPAN_ATTRS][key] = value
        tracing_context[constants.MAGENTIC_SPAN_ATTRS][constants.CLIENT_NAME_KEY] = self._tracing_initializer.service_name
        return tracing_context

    def _create_carrier(self) -> dict:
        headers = self.headers
        if headers:
            return headers
        source = self._get_details() if self.is_event_bridge_event else self.main_event_data
        return source.get(constants.OTEL_TRACE_CONTEXT_KEY, {})

    def _create_payload(self) -> dict:
        if self.is_state_machine_event and self._is_state_machine_start_event():
            return self.event.get(constants.STATE_MACHINE_ORIGINAL_PAYLOAD_KEY, {})
        return self.event
    
    def _is_state_machine_start_event(self) -> bool:
        return self.event.get(constants.MAGENTIC_SPAN_ATTRS, {}).get(constants.STATE_MACHINE_START_EVENT_KEY, False)

    @staticmethod
    def _extract_account_id_from_arn(arn: Optional[str]) -> Optional[str]:
        if arn:
            parts = arn.split(':')
            if len(parts) > 4:
                return parts[4]
        return None

    @staticmethod
    def _extract_region_from_arn(arn: Optional[str]) -> Optional[str]:
        if arn:
            parts = arn.split(':')
            if len(parts) > 3:
                return parts[3]
        return None
    
    @property
    def headers(self) -> Dict[str, str]:
        headers = self.event.get("headers", {}) or {}
        headers = {k.lower(): v for k, v in headers.items()}
        multi_value_headers = self.event.get("multiValueHeaders", {})
        if isinstance(multi_value_headers, dict):
            headers.update(
                {
                    k.lower(): ", ".join(v) if isinstance(v, list) else ""
                    for k, v in multi_value_headers.items()
                }
            )

        return headers