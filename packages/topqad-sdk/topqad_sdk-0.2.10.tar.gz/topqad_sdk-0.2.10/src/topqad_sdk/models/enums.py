from enum import Enum


class StatusEnum(str, Enum):
    """Status values for circuit processing."""

    waiting = "waiting"
    done = "done"
    executing = "executing"
    failed = "failed"


class StartStepEnum(str, Enum):
    """Start step options for circuit processing."""

    DECOMPOSER = "decomposer"
    OPTIMIZER = "optimizer"
    SCHEDULER = "scheduler"


class LayoutType(str, Enum):
    """Layout type options."""

    HLA = "HLA"
    CUSTOM = "custom"
