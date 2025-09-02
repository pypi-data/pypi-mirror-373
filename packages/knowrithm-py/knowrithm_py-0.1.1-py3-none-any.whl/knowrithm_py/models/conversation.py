
import enum


class ConversationStatus(enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class EntityType(enum.Enum):
    USER = 'user'
    LEAD = 'lead'
