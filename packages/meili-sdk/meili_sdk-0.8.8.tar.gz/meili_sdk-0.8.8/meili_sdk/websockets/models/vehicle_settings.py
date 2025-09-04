from meili_sdk.models.base import BaseModel

__all__ = ("VehicleSettingsMessage",)


class VehicleSettingsMessage(BaseModel):
    message_frequency: float
