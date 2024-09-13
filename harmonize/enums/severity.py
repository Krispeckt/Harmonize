from enum import Enum


class Severity(Enum):
    """
    Represents errors severity levels from lavalink.
    """
    COMMON = "common"
    SUSPICIOUS = "suspicious"
    FAULT = "fault"
