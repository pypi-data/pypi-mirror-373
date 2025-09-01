from enum import Enum


class RunStatus(str, Enum):
    CANCELLED = "cancelled"
    ERROR = "error"
    RUNNING = "running"
    SCHEDULING = "scheduling"
    SUCCESS = "success"

    def __str__(self) -> str:
        return str(self.value)
