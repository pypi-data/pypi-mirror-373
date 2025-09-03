
SERVICE_NAME_ENV_NAME = "OTEL_SERVICE_NAME"

OTEL_TRACE_CONTEXT_KEY = 'x-magentic-context'
CLIENT_NAME_KEY = 'client_service_name'
CLIENT_ARN_KEY = 'client_service_arn'

MAGENTIC_SPAN_ATTRS = 'x-magentic-span-attrs'
SERVERLESS_SYSTEM_KEY = 'x-serverless-system'
STATE_MACHINE = 'StateMachine'
EVENT_BRIDGE = 'EventBridge'
STATE_MACHINE_ORIGINAL_PAYLOAD_KEY = 'original_input'
STATE_MACHINE_NAME_KEY = 'aws.state_machine'
STATE_MACHINE_START_EVENT_KEY = 'aws.state_machine.is_start'

AWS_EVENT_BRIDGE_BUS_KEY = 'aws.eventbridge.bus'
AWS_EVENT_BRIDGE_SOURCE_KEY = 'aws.eventbridge.source'
AWS_EVENT_BRIDGE_DETAIL_TYPE_KEY = 'aws.eventbridge.detail_type'
AWS_EVENT_BRIDGE_BUS_ARN  = 'aws.eventbridge.bus_arn'


AWS_APP_SYNC_API_NAME = 'aws.appsync.api'
AWS_APP_SYNC_API_ARN = 'aws.appsync.api_arn'

IGNORE_PROPAGATION_KEYS = [STATE_MACHINE_START_EVENT_KEY, AWS_EVENT_BRIDGE_BUS_KEY,
                           AWS_EVENT_BRIDGE_SOURCE_KEY, AWS_EVENT_BRIDGE_DETAIL_TYPE_KEY,
                           AWS_EVENT_BRIDGE_BUS_ARN, AWS_APP_SYNC_API_NAME]
