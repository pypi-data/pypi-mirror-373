from enum import StrEnum


class ExecutionStatus(StrEnum):
    COLLECTED = "collected"
    STARTED = "started"
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    FAILED_SKIPPED = "failed-skipped"  # Force skipped, used in fail2skip plugin
