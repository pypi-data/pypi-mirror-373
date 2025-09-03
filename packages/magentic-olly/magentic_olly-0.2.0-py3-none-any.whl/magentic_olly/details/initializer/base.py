from abc import ABC
from typing import Optional
from opentelemetry.sdk.resources import Resource
from ..model import model


class BaseInitializer(ABC):
    def __init__(self, params: model.InstrumentationParams):
        self._params = params
    
    
    def initialize(self):
        raise NotImplementedError("Subclasses must implement this method")
    
    def _create_resource(self, service_name: Optional[str] = None) -> Resource:
        resource_attributes = {"service.name": service_name or self._params.service_name,
                               "service.environment": self._params.system_environment or "Unknown"}
        resource = Resource.create(resource_attributes)
        return resource