from enum import Enum


class ConfigPropertyPropertyType(str, Enum):
    BOOLEAN = "BOOLEAN"
    ENCRYPTEDSTRING = "ENCRYPTEDSTRING"
    INTEGER = "INTEGER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    TIMESTAMP = "TIMESTAMP"
    URL = "URL"
    UUID = "UUID"

    def __str__(self) -> str:
        return str(self.value)
