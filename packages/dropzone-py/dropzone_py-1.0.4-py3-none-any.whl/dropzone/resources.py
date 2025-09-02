from .exceptions import BadRequest, NoUserOnApiKey, AccessDenied, SystemError, SystemNotReady, ContextItemNotFound

# Constants
EXCEPTIONS = {400: BadRequest, 401: NoUserOnApiKey, 403: AccessDenied, 404: ContextItemNotFound, 500: SystemError, 503: SystemNotReady}
SCHEMA_TYPES = ["CanceledEnum", "FullAlert", "HandlerVersionEnum", "Investigation", "NullEnum", "OutcomeEnum", "PriorityEnum", "StatusEnum"]

class Feedback:
    STATUS_TYPES = ["in_review", "reviewed"]
    OUTCOME_TYPES = ["COMPLETED_BREACHED_CONFIRMED", "COMPLETED_BREACHED_SUSPICIOUS", "COMPLETED_FALSE_ALERT",
                     "INCOMPLETE", "IGNORED"]
    PRIORITY_TYPES = ["informational", "notable", "urgent"] 