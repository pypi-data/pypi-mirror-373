import os
from enum import Enum
from typing import List, Optional
from typing import Optional
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from .settings import settings

class ExportMode(Enum):
    CONSOLE = "CONSOLE"
    HTTP = "HTTP"
    GRPC = "GRPC"

class ResourceType(Enum):
    LAMBDA = "Lambda"
    STATE_MACHINE = "StateMachine"
    EVENT_BRIDGE = "EventBridge"
    APP_SYNC = "AppSync"
    PROXY = "Proxy"
    
       
class InstrumentationParams:
    def __init__(
        self,
        service_name: Optional[str] = None,
        system_environment: Optional[str] = None,
        export_server_url: Optional[str] = None,
        export_server_token: Optional[str] = None,
        export_mode: Optional[ExportMode] = None,
        extra_instrumentors: Optional[List[BaseInstrumentor]] = None,
        enable_logging: Optional[bool] = False,
        propagate_context: Optional[bool] = False,
    ):
        self.service_name = settings.magentic_service_name or service_name
        self.export_server_url = settings.magentic_export_server_url or export_server_url
        self.export_server_token = settings.magentic_export_server_token or export_server_token
        self.extra_instrumentors = extra_instrumentors if extra_instrumentors is not None else []
        self.enable_logging = enable_logging
        self.propagate_context = propagate_context
        self.system_environment = settings.magentic_system_environment or system_environment
        self.export_mode = export_mode
        if export_mode is None:
            if export_server_url is None:
                self.export_mode = ExportMode.CONSOLE
            else:
                self.export_mode = ExportMode.GRPC

    def __repr__(self):
        return (
            f"InstrumentationParams(service_name={self.service_name}, "
            f"system_environment={self.system_environment}, "
            f"export_server_url={self.export_server_url}, "
            f"export_server_token={'***' if self.export_server_token else None}, "
            f"export_mode={self.export_mode}, "
            f"enable_logging={self.enable_logging}, "
            f"propagate_context={self.propagate_context})"
        )

