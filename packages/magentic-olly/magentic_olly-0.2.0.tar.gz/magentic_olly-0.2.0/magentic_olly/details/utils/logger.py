import logging
from ..model import settings

class MagenticLogger(logging.Logger):
    def __init__(self, name: str):
        super().__init__(name)
        self.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        self.addHandler(handler)
    
    def _log(self, level, msg, args, exc_info = None, extra = None, stack_info = False, stacklevel = 1):
        if not settings.magentic_verbose_logging:
            return
        return super()._log(level, msg, args, exc_info, extra, stack_info, stacklevel)
    


magentic_logger = MagenticLogger("opentelemetry.magentic_olly")