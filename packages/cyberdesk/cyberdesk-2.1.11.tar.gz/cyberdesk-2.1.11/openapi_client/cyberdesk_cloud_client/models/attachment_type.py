from enum import Enum


class AttachmentType(str, Enum):
    INPUT = "input"
    OUTPUT = "output"

    def __str__(self) -> str:
        return str(self.value)
