import typing as t

from meili_sdk.exceptions import MissingAttributesException, ValidationError
from meili_sdk.models.base import BaseModel
from meili_sdk.utils import VehicleCurrentSubtask
from meili_sdk.websockets.constants import (
    ALL,
    EVENT_BATTERY,
    EVENT_CONNECT,
    EVENT_DOCKING_ROUTINE,
    EVENT_GOAL_STATUS,
    EVENT_LOCATION,
    EVENT_MAP_UPDATE,
    EVENT_NEW_MISSION,
    EVENT_NOTIFICATION,
    EVENT_PATH_DATA,
    EVENT_SPEED,
    EVENT_STATE,
    EVENT_TOPIC_DATA,
    EVENT_TOPICS_LIST,
    EVENT_VEHICLE_LOADSET_DATA,
)

__all__ = ("Message",)


class Message(BaseModel):
    """
    Message to be sent via websocket

    Some pre-sending validation is done here
    """

    event: str
    value: t.Optional[dict] = None
    vehicle: t.Optional[str] = None
    vehicles: t.Optional[t.List[str]] = None

    def __init__(self, *, event, **kwargs) -> None:
        if event not in ALL:
            raise ValueError("Invalid event")

        if event == EVENT_CONNECT:
            if "vehicles" not in kwargs:
                raise MissingAttributesException(self.__class__, "vehicles")
            kwargs["value"] = 1  # required to call validation for only existing values
        else:
            if "vehicle" not in kwargs:
                raise MissingAttributesException(self.__class__, "vehicles")
            if "value" not in kwargs:
                raise MissingAttributesException(self.__class__, "value")

        if event == EVENT_GOAL_STATUS:
            current_vehicle_subtask = VehicleCurrentSubtask()
            try:
                kwargs["value"]["subtask_uuid"] = current_vehicle_subtask[
                    kwargs["vehicle"]
                ]
            except (KeyError, AttributeError):
                pass

        kwargs["event"] = event
        super().__init__(**kwargs)

    def validate_value(self):
        value = self.value
        event = self.event

        {
            EVENT_DOCKING_ROUTINE: self._validate_value_for_docking_routine,
            EVENT_CONNECT: self._validate_value_for_registration,
            EVENT_LOCATION: self._validate_value_for_location,
            EVENT_SPEED: self._validate_value_for_speed,
            EVENT_BATTERY: self._validate_value_for_battery,
            EVENT_GOAL_STATUS: self._validate_value_for_goal_status,
            EVENT_NOTIFICATION: self._validate_value_for_notification,
            EVENT_TOPICS_LIST: self._validate_value_for_topics_list,
            EVENT_TOPIC_DATA: self._validate_value_for_topic_data,
            EVENT_PATH_DATA: self._validate_value_for_path_data,
            EVENT_STATE: self._validate_value_for_status,
            EVENT_MAP_UPDATE: self._validate_value_for_map_update,
            EVENT_NEW_MISSION: self._validate_value_for_new_mission,
            EVENT_VEHICLE_LOADSET_DATA: self._validate_value_for_vehicle_loadset_data,
        }[event](value)
        return value

    @staticmethod
    def _validate_value_for_docking_routine(value):
        try:
            path = value["path"]
        except KeyError:
            raise ValidationError(f"Missing properties: path")

        if not isinstance(path, (list, set, tuple)):
            raise ValidationError("path needs to be a list of lists")

        for index, path_point in enumerate(path):
            if not isinstance(path_point, (list, set, tuple)):
                raise ValidationError(
                    f"error at index: {index}: path needs to be a list of lists"
                )
            if len(path_point) != 2:
                raise ValidationError(
                    f"error at index: {index} {path_point}: every path point needs to be a tuple of 2 coordinates"
                )

    def _validate_value_for_registration(self, _):
        vehicles = self.vehicles

        if not isinstance(vehicles, (list, tuple, set)):
            raise ValidationError("Vehicles requires an iterable type")

    @staticmethod
    def _validate_value_for_location(value):
        sets = (
            {"x", "y"},
            {"xm", "ym"},
            {"lat", "lon"},
        )
        given_keys = set(value.keys())

        if not any([len(key_set - given_keys) == 0 for key_set in sets]):
            raise ValidationError(
                f"Location value needs to have one of the following full pairs: (x,y), (xm, ym) or (lat, lon)"
            )

    @staticmethod
    def _validate_value_for_speed(value):
        try:
            value["speed"]
        except KeyError:
            raise ValidationError(f"Missing properties: speed")

    def _validate_value_for_battery(self, value):
        pass

    @staticmethod
    def _validate_value_for_goal_status(value):
        missing_keys = {"status_id", "goal_id"} - set(value.keys())
        if len(missing_keys) > 0:
            raise ValidationError(f"Missing keys: {', '.join(missing_keys)}")

    @staticmethod
    def _validate_value_for_topics_list(value):
        if not isinstance(value, list):
            raise ValidationError("Value needs to be a list")
        for val in value:
            if not isinstance(val, dict):
                raise ValidationError("Each item in value needs to be a dictionary")

            missing_keys = {"topic", "messageType"} - val.keys()

            if len(missing_keys) > 0:
                raise ValidationError(f"Missing properties: {', '.join(missing_keys)}")

    def _validate_value_for_topic_data(self, value):
        pass

    @staticmethod
    def _validate_value_for_path_data(value):
        try:
            path = value["path"]
        except KeyError:
            raise ValidationError(f"Missing properties: path")

        if not isinstance(path, (list, set, tuple)):
            raise ValidationError("path needs to be a list of lists")

        for index, path_point in enumerate(path):
            if not isinstance(path_point, (list, set, tuple)):
                raise ValidationError(
                    f"error at index: {index}: path needs to be a list of lists"
                )
            if len(path_point) != 2:
                raise ValidationError(
                    f"error at index: {index} {path_point}: every path point needs to be a tuple of 2 coordinates"
                )

    @staticmethod
    def _validate_value_for_notification(value):
        try:
            level = value["level"]
        except KeyError:
            raise ValidationError("Missing properties: level")

        if level not in ["info", "error", "warning"]:
            raise ValidationError(
                "level needs to be one of the following: info, error, warning"
            )

        try:
            message = value["message"]
        except KeyError:
            raise ValidationError(f"Missing properties: message")

        if not isinstance(message, str):
            raise ValidationError("message needs to be a string")

        if len(message) > 255:
            raise ValidationError("message needs to be less than 255 characters")

    def _validate_value_for_status(self, value):
        try:
            self._validate_value_for_location(value["location"])
            self._validate_value_for_speed(value["speed"])
            if "battery" in value:
                self._validate_value_for_battery(value["battery"])

        except Exception as e:
            raise ValidationError("Missing property location, battery or speed")

    @staticmethod
    def _validate_value_for_map_update(value):
        unexpected_keys = set(value.keys()) - {"stations", "paths", "zones", "presets"}
        if len(unexpected_keys) > 0:
            raise ValidationError(
                f"Received unexpected keys: {', '.join(unexpected_keys)}"
            )

    @staticmethod
    def _validate_value_for_new_mission(value):
        try:
            value["subtasks"]
        except KeyError:
            raise ValidationError("Missing properties: subtasks")

    @staticmethod
    def _validate_value_for_vehicle_loadset_data(value):
        try:
            loads = value["loads"]
        except KeyError:
            raise ValidationError("Missing properties: loads")

        if not isinstance(loads, (list, tuple, set)):
            raise ValidationError("Loads needs to be an iterable")

        for load in loads:
            try:
                load["load_id"]
            except KeyError:
                raise ValidationError("Missing properties: load_id")

            try:
                load["weight"]
            except KeyError:
                raise ValidationError("Missing properties: weight")
