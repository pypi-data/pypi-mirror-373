from datetime import datetime

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel
from meili_sdk.version import VERSION

CURRENT_HEADER_ID = 0


class VDA5050ConnectionMessage(BaseModel):
    manufacturer: str
    serialNumber: str
    timestamp: datetime
    headerId: int
    version: str
    connectionState: str

    def __init__(self, **kwargs):
        global CURRENT_HEADER_ID
        CURRENT_HEADER_ID += 1
        kwargs.setdefault("timestamp", datetime.now())
        kwargs.setdefault("headerId", CURRENT_HEADER_ID)
        kwargs.setdefault("version", VERSION)

        super().__init__(**kwargs)
