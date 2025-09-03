from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    magentic_service_name: Optional[str] = None
    magentic_system_environment: Optional[str] = None
    magentic_export_server_url: Optional[str] = None
    magentic_export_server_token: Optional[str] = None
    
    magentic_instrumentation_enabled: Optional[bool] = True
    magentic_logging_enabled: Optional[bool] = True
    magentic_tracing_enabled: Optional[bool] = True
    magentic_verbose_logging: Optional[bool] = False
    
    magentic_logging_export_mode: Optional[int] = None
    magentic_tracing_export_mode: Optional[int] = None
    magentic_tracing_export_timeout: Optional[int] = 250
    magentic_logging_export_timeout: Optional[int] = 250

settings = Settings()
