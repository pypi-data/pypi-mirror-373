class Status:
    SKIPPED = "SKIPPED"
    FAILED = "FAILED"
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"


class Queue:
    SHORT = "core-short"
    MEDIUM = "core-medium"
    LONG = "core-long"

    # Legacy
    CORE = "core"
    EMS = "ems"
    SIERRA = "sierra"


class Tasks:
    SEND_VERSION = "send_version_to_core"
    UPDATE_TASK_STATUS = "update_task_status"
    UPDATE_TASK_VALUES = "update_task_values"
    MODEL_UPDATE = "component_model_update"
    RUN_POST_TASK_COMPLETION_TASKS = "run_post_task_completion_tasks"
    PURGE_MODELS = "purge_unused_models"


class Models:
    IMAGE_CLASSIFIER = "Pildid"

    TOPIC_KEYWORDS_ET = "Teemamärksõnad (ET)"
    TOPIC_KEYWORDS_EN = "Teemamärksõnad (EN)"

    FORM_KEYWORDS_ET = "Vormimärksõnad (ET)"
    FORM_KEYWORDS_EN = "Vormimärksõnad (EN)"

    TIME_KEYWORDS_ET = "Ajamärksõnad (ET)"
    TIME_KEYWORDS_EN = "Ajamärksõnad (EN)"

    UDK_ET = "UDK (ET)"
    UDK_EN = "UDK (EN)"
    UDC_ET = "UDC (ET)"
    UDC_EN = "UDC (EN)"

    DOMAIN_KEYWORDS_ET = "Märksõnade valdkonnad (ET)"
    DOMAIN_KEYWORDS_EN = "Märksõnade valdkonnad (EN)"
