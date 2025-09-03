from opentelemetry.trace import SpanKind, Status, StatusCode

class SpansUtils:
    @staticmethod
    def set_span_response_attributes(span, response):
        if not response or not isinstance(response, dict):
            return
        status_code = response.get("statusCode", None)
        if status_code is None or not isinstance(status_code, (int, str)):
            return
        if isinstance(status_code, int) and status_code >= 400:
            span.set_status(Status(StatusCode.ERROR))
        else:
            span.set_status(Status(StatusCode.OK))
        span.set_attribute("response.status_code", str(status_code))

    @classmethod
    def set_span_magentic_attributes(cls, span, params):
        if not params.has_magentic_span_attrs:
            return
        attrs = params.magentic_span_attrs
        for key, value in attrs.items():
            cls.set_span_attribute(span, key, value)
    
    @staticmethod    
    def set_span_attribute(span, key, value):
        if not span or not key:
            return
        if value is None or isinstance(value, (dict, list, tuple)):
            return
        span.set_attribute(key, str(value))