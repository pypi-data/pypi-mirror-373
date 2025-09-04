from enum import Enum


class ProjectClassifier(str, Enum):
    APPLICATION = "APPLICATION"
    CONTAINER = "CONTAINER"
    DATA = "DATA"
    DEVICE = "DEVICE"
    DEVICE_DRIVER = "DEVICE_DRIVER"
    FILE = "FILE"
    FIRMWARE = "FIRMWARE"
    FRAMEWORK = "FRAMEWORK"
    LIBRARY = "LIBRARY"
    MACHINE_LEARNING_MODEL = "MACHINE_LEARNING_MODEL"
    NONE = "NONE"
    OPERATING_SYSTEM = "OPERATING_SYSTEM"
    PLATFORM = "PLATFORM"

    def __str__(self) -> str:
        return str(self.value)
