
import enum


class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class UserRole(enum.Enum):
    SUPER_ADMIN="super_admin"
    ADMIN="admin"
    USER="user"
