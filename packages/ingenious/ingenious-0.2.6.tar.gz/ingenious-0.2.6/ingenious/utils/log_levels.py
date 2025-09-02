from typing import Dict, Optional


class LogLevel:
    DEBUG: int = 0
    INFO: int = 1
    WARNING: int = 2
    ERROR: int = 3

    @staticmethod
    def from_string(level_str: str) -> Optional[int]:
        level_mapping: Dict[str, int] = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
        }
        return level_mapping.get(str(level_str).upper(), None)

    @staticmethod
    def to_string(level: int) -> str:
        level_mapping: Dict[int, str] = {
            LogLevel.DEBUG: "DEBUG",
            LogLevel.INFO: "INFO",
            LogLevel.WARNING: "WARNING",
            LogLevel.ERROR: "ERROR",
        }
        return level_mapping.get(level, "Unknown")
