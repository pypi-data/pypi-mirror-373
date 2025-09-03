from enum import Enum


class Role(str, Enum):
    ACCOUNT = "account"
    AGENT = "agent"
    SYSTEM = "system"
