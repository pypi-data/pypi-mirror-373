from enum import StrEnum


class LifecycleTimestamp(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class StatusTimestamp(StrEnum):
    DELETED_AT = "deleted_at"
    RESTORED_AT = "restored_at"
    DEACTIVATED_AT = "deactivated_at"
    ACTIVATED_AT = "activated_at"


class DataTimestamp(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DELETED_AT = "deleted_at"
    RESTORED_AT = "restored_at"
    DEACTIVATED_AT = "deactivated_at"
    ACTIVATED_AT = "activated_at"
