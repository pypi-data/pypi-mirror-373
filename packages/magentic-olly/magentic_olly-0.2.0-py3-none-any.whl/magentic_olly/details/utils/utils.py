
class Utils:
    @staticmethod
    def extract_event_and_context(args, kwargs):
        event = kwargs.get('event', None)
        context = kwargs.get('context', None)
        if event is None and len(args) > 0:
            event = args[0]
        if context is None and len(args) > 1:
            context = args[1]
        return event, context