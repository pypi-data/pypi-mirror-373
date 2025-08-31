from typing import TypedDict

class EventConfig(TypedDict):
    eventType: str
    webhookListener: str

EVENT_CONFIGS: dict[str, EventConfig] = {
    "queryCreated": {
        "eventType": "QUERY_CREATED",
        "webhookListener": "emitQueryCreated",
    },
    "queryCompleted": {
        "eventType": "QUERY_COMPLETED",
        "webhookListener": "emitQueryCompleted",
    },
    "queryFailed": {
        "eventType": "QUERY_FAILED",
        "webhookListener": "emitQueryFailed",
    },
    "eventCreated": {
        "eventType": "EVENT_CREATED",
        "webhookListener": "emitEventCreated",
    },
}
