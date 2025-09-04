import sys

if sys.version_info > (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = ("Config",)


class Config(TypedDict):
    uuid: str

    fleet: str
    mqttId: str
    token: str
    version: int
    timestamp: str
    site: str
