import typing as t

from meili_sdk.models.base import BaseModel
from meili_sdk.websockets.models import ActionDefinition, Path, Preset, Station

__all__ = ("UpdateMapMessage", "YamlFile")


class YamlFile(BaseModel):
    resolution: float
    mode: str
    origin: t.List
    negate: int
    occupied_thresh: float
    free_thresh: float


class UpdateMapMessage(BaseModel):
    uuid: str
    displayable_image: t.Optional[str]
    yaml_file: t.Optional[YamlFile]
    width: t.Optional[int]
    height: t.Optional[int]
    stations: t.Optional[t.List[Station]]
    paths: t.Optional[t.List[Path]]
    presets: t.Optional[t.List[Preset]]
    action_definitions: t.Optional[t.List[ActionDefinition]]


class ConfirmMapMessage(BaseModel):
    stations: t.Optional[t.List[Station]]
    paths: t.Optional[t.List[Path]]
    presets: t.Optional[t.List[Preset]]
