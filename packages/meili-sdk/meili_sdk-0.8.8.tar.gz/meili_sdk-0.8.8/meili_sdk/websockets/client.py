import json
import logging
import os
import re
import ssl
import threading
import time
import typing as t

import websocket

from meili_sdk.exceptions import (
    MeiliCriticalException,
    MeiliException,
    WebsocketException,
)
from meili_sdk.resources.base import BaseResource
from meili_sdk.site import get_host
from meili_sdk.utils import VehicleCurrentSubtask
from meili_sdk.version import VERSION
from meili_sdk.websockets import constants
from meili_sdk.websockets.models import CancelTaskMessage, DockingRoutineMessage
from meili_sdk.websockets.models.message import Message
from meili_sdk.websockets.models.move_message import MoveMessage
from meili_sdk.websockets.models.task_v2 import process_task_v2_message
from meili_sdk.websockets.models.topic import RosTopic
from meili_sdk.websockets.models.traffic_control_action_message import (
    PathReroutingMessage,
    SlowDownMessage,
    process_clearance_data,
)
from meili_sdk.websockets.models.update_map_message import (
    ConfirmMapMessage,
    UpdateMapMessage,
)
from meili_sdk.websockets.models.vehicle_settings import VehicleSettingsMessage

logger = logging.getLogger("meili_sdk")

__all__ = ("MeiliWebsocketClient",)


class MeiliWebsocketClient:
    """
    Client for all communication related with FMS through websockets

    :Parameters:
    token (str) - authentication token with the WS
    fleet (bool) - use fleet websocket if set to true (default: true)
    open_handler() (callable) - a callable object that will be called with no parameters when websocket is opened
    close_handler() (callable) - a callable objects that will be called with no parameters when websocket is closed
    error_handler(err) (callable) - a callable with a single parameter that will receive the exception as a parameter
    docking_routine_request_handler(message: DockingRoutineMessage, vehicle: str) (callable) - a callable with a single parameter that will receive the message as a parameter
    docking_routine_finalize_handler(message: DockingRoutineMessage, vehicle: str) (callable) - a callable with a single parameter that will receive the message as a parameter
    move_action_handler(message: MoveMessage, data: dict, vehicle: str) - a callable for moving vehicle according to FMS
    slow_down_handler(message: SlowDownMessage, data: dict, vehicle: str) - a callable for altering movement of robots
    path_rerouting_handler(message: path_rerouting_handler, data: dict, vehicle: str) - a callable for altering path of robots
    collision_clearance_handler(message: collision_clearance_handler, data: dict, vehicle: str) - a callable for clearing the collision messages
    topic_list_handler(data: dict, vehicle: str) - a callable for handling topic list request
    topic_list_initializer_handler(topics: List[RosTopic], data: dict, vehicle: str) - a callable to initialize topics
    """

    __vehicles = []
    __connection: t.Optional[websocket.WebSocketApp]
    thread: threading.Thread

    def __init__(
        self,
        token: str,
        override_host: t.Optional[str] = None,
        fleet: t.Optional[bool] = True,
        open_handler: t.Optional[t.Callable] = None,
        close_handler: t.Optional[t.Callable] = None,
        error_handler: t.Optional[t.Callable] = None,
        docking_routine_request_handler: t.Optional[t.Callable] = None,
        docking_routine_finalize_handler: t.Optional[t.Callable] = None,
        task_v2_handler: t.Optional[t.Callable] = None,
        task_cancellation_handler: t.Optional[t.Callable] = None,
        move_action_handler: t.Optional[t.Callable] = None,
        slow_down_handler: t.Optional[t.Callable] = None,
        path_rerouting_handler: t.Optional[t.Callable] = None,
        collision_clearance_handler: t.Optional[t.Callable] = None,
        topic_list_handler: t.Optional[t.Callable] = None,
        topic_list_initializer_handler: t.Optional[t.Callable] = None,
        fake_opened_connection: t.Optional[bool] = False,
        message_error_handler: t.Optional[t.Callable] = None,
        update_map_handler: t.Optional[t.Callable] = None,
        vehicle_initial_position_handler: t.Optional[t.Callable] = None,
        update_vehicle_settings: t.Optional[t.Callable] = None,
        pause_task_handler: t.Optional[t.Callable] = None,
        resume_task_handler: t.Optional[t.Callable] = None,
        remove_vehicle_from_fleet_handler: t.Optional[t.Callable] = None,
        set_initial_position_handler: t.Optional[t.Callable] = None,
        update_map_id_handler: t.Optional[t.Callable] = None,
    ) -> None:
        self.token = token
        self.skip_tls = os.getenv("SKIP_TLS", False)  # if True WS will skip TLS
        self.__connection_is_open = fake_opened_connection
        self.__fleet = fleet

        host = override_host or get_host()
        self.url = BaseResource.build_url(
            host, f"ws/{'fleets/' if fleet else 'vehicle/'}"
        )

        self.__open_handler = open_handler
        self.__close_handler = close_handler
        self.__error_handler = error_handler

        self.__docking_routine_request_handler = docking_routine_request_handler
        self.__docking_routine_finalize_handler = docking_routine_finalize_handler
        self.__task_v2_handler = task_v2_handler
        self.__task_cancellation_handler = task_cancellation_handler
        self.__move_handler = move_action_handler
        self.__slow_down_handler = slow_down_handler
        self.__path_rerouting_handler = path_rerouting_handler
        self.__collision_clearance_handler = collision_clearance_handler
        self.__topic_list_handler = topic_list_handler
        self.__topic_list_initializer_handler = topic_list_initializer_handler
        self.__message_error_handler = message_error_handler
        self.__update_map_handler = update_map_handler
        self.__update_vehicle_settings = update_vehicle_settings
        self.__pause_task_handler = pause_task_handler
        self.__resume_task_handler = resume_task_handler
        self.__set_initial_position_handler = set_initial_position_handler
        self.__connection = None
        self.__vehicle_initial_position_handler = vehicle_initial_position_handler
        self.__remove_vehicle_from_fleet_handler = remove_vehicle_from_fleet_handler
        self.__update_map_id_handler = update_map_id_handler

    def get_headers(self) -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (platform; rv:gecko-version) Gecko/gecko-trail Firefox/firefox-version",
            "x-meili-app-name": "sdk",
            "x-meili-app-version": VERSION,
            "x-meili-fleet-token": self.token,
        }

    def run_in_thread(self, wait_to_connect=True):
        try:
            self.thread = threading.Thread(
                target=self.run, args=(), kwargs={"loop": True}, daemon=True
            )
            self.thread.start()

            if wait_to_connect:
                while not self.__connection_is_open:
                    continue
        except RuntimeError as exc:
            raise MeiliException(f"Cannot start websocket thread: {exc}")

    def run(self, loop=False):
        self._reconnect()

        if loop:
            while True:
                if self.skip_tls:
                    self.__connection.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                else:
                    self.__connection.run_forever()
                time.sleep(2)

        else:
            self.__connection.run_forever()

    def _reconnect(self):
        if self.__connection and isinstance(self.__connection, websocket.WebSocketApp):
            self.__connection.close()
        self.__connection = websocket.WebSocketApp(
            self.url,
            on_close=self.__on_close,
            on_open=self.__on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            header=self.get_headers(),
        )

    def __on_open(self, _):
        self.__connection_is_open = True
        self.on_open()

    def on_open(self):
        """
        When websocket is opened it should send a registration message to backend in order
        to set the vehicles that will be connected via this websocket
        """
        registration_message = self._get_registration_message()
        self.send(registration_message)

        if self.__open_handler and callable(self.__open_handler):
            self.__open_handler()

    def __on_close(self, _, code, __):
        self.__connection_is_open = False
        self.on_close()
        if code in constants.FleetConsumerCodes.ALL:
            self.on_error(
                self.__connection,
                MeiliCriticalException(
                    f"Connection closed with custom code {code}. ",
                    constants.FleetConsumerCodes.TEXT[code],
                ),
            )

    def on_close(self):
        if self.__close_handler:
            self.__close_handler()

    def on_message(self, _, message):
        """
        Capture message, try loading JSON and pass it to message handler
        """
        try:
            message = json.loads(message)
            action = message["type"]
        except (ValueError, json.JSONDecodeError) as e:
            raise WebsocketException(f"Cannot decode JSON from response message: {e}")
        except KeyError:
            raise WebsocketException(f"Cannot retrieve message type")
        else:
            vehicle = message.get("vehicle", None)

            if action in constants.IGNORED_TYPES:
                return

            if action == constants.ACTION_ERROR:
                self.process_message_error(message)
                return

            if not vehicle and self.__fleet and action in constants.ALL_ACTIONS:
                raise WebsocketException(
                    f"Malformed message received. No vehicle in a fleet connection: {message}"
                )
            self.process_message(action, message, vehicle)

    def on_error(self, connection, error):
        logger.warning(f"An error has occurred inside the websocket client: {error}")
        if self.__error_handler:
            self.__error_handler(connection, error)

    def send(self, message: t.Union[dict, list, Message, str]):
        """
        Send message to the backend server

        Will automatically resolve message into required data type
        """
        if not self.__connection_is_open:
            raise WebsocketException("Connection is closed")
        if isinstance(message, Message):
            message = dict(message)
        if not isinstance(message, str):
            message = json.dumps(message)
        self.send_raw(message)

    def send_raw(self, message, timeout=1):
        try:
            self.__connection.send(message)
        except websocket.WebSocketException as e:
            logger.warning(f"Failed to send message due to {e}. Reconnecting...")
            self._reconnect()
            time.sleep(timeout)
            self.send_raw(message, timeout + 1)

    def process_message(
        self, action: str, message: dict, vehicle: t.Optional[str] = None
    ):
        processors = {
            constants.ACTION_DOCKING_ROUTINE_REQUEST: self.process_docking_routine_request,
            constants.ACTION_DOCKING_ROUTINE_FINALIZE: self.process_docking_routine_finalize,
            constants.ACTION_TASK_V2: self.process_task_v2,
            constants.ACTION_TASK_CANCELLATION: self.process_task_cancellation,
            constants.ACTION_MOVE: self.process_move,
            constants.ACTION_MOVE_TO_CHARGING_POINT: self.process_move,
            constants.ACTION_SLOW_DOWN: self.process_slow_down,
            constants.ACTION_PATH_REROUTING: self.process_path_rerouting,
            constants.ACTION_COLLISION_CLEARANCE: self.process_collision_clearance,
            constants.ACTION_TOPIC_LIST: self.process_request_for_topics,
            constants.ACTION_TOPIC_INITIALIZATION: self.process_topic_list,
            constants.ACTION_UPDATE_MAP: self.process_update_map,
            constants.ACTION_UPDATE_VEHICLE_SETTINGS: self.process_update_vehicle_settings,
            constants.ACTION_PAUSE_TASK: self.process_pause_task,
            constants.ACTION_RESUME_TASK: self.process_resume_task,
            constants.ACTION_SET_INITIAL_POSITION: self.process_set_initial_position,
            constants.ACTION_UPDATE_MAP_ID: self.process_update_map_id,
        }
        try:
            processor = processors[action]
        except KeyError:
            logger.warning(
                f"Cannot handle action {action}. Maybe you are using an outdated library?"
            )
            return

        if processor and callable(processor):
            processor(message, vehicle)

    def process_set_initial_position(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        set_initial_position_msg = message["data"]
        if self.__set_initial_position_handler and callable(
            self.__set_initial_position_handler
        ):
            self.__set_initial_position_handler(vehicle, set_initial_position_msg)

    def process_update_map_id(self, message: dict, vehicle: t.Optional[str] = None):
        map_id_msg = message["data"]
        if self.__update_map_id_handler and callable(self.__update_map_id_handler):
            self.__update_map_id_handler(map_id_msg, vehicle)

    def process_resume_task(self, message: dict, vehicle: t.Optional[str] = None):
        # First data would be read but it is empty
        resume_task = {}
        if self.__resume_task_handler and callable(self.__resume_task_handler):
            self.__resume_task_handler(resume_task, vehicle)

    def process_pause_task(self, message: dict, vehicle: t.Optional[str] = None):
        # First data would be read but it is empty
        pause_task = {}
        if self.__pause_task_handler and callable(self.__pause_task_handler):
            self.__pause_task_handler(pause_task, vehicle)

    def process_update_vehicle_settings(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        update_vehicle_settings = VehicleSettingsMessage(**message["data"])
        frequency = update_vehicle_settings.message_frequency
        if self.__update_vehicle_settings and callable(self.__update_vehicle_settings):
            self.__update_vehicle_settings(frequency, vehicle)

    def process_update_map(self, message: dict, vehicle: t.Optional[str] = None):
        """
        A method to trigger a map update handler if it is provided by the meili agent or integrator
        """
        status = message.get("status", constants.MapUpdateMessageStatuses.UPDATE)
        if status == constants.MapUpdateMessageStatuses.CONFIRM:
            data = message["data"]
            if "areas" in data: # For new format divided by areas
                # TODO: Temporary fix for new area-based structure that will keep current integrations working.
                # Needs redesign for proper area management, along with integration
                combined_data = {
                    "stations": [],
                    "paths": [],
                    "presets": []
                }
                for area in data["areas"]:
                    combined_data["stations"].extend(area.get("stations", []))
                    combined_data["paths"].extend(area.get("paths", []))
                    combined_data["presets"].extend(area.get("presets", []))
                update_map_message = ConfirmMapMessage(**combined_data)
            else: # Legacy: Old format without areas
                update_map_message = ConfirmMapMessage(**data)
        else:
            update_map_message = UpdateMapMessage(**message["data"])

        if self.__update_map_handler and callable(self.__update_map_handler):
            self.__update_map_handler(update_map_message, vehicle, status)

    def process_docking_routine_request(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        dock_message = DockingRoutineMessage(**message["data"])
        if self.__docking_routine_request_handler and callable(
            self.__docking_routine_request_handler
        ):
            self.__docking_routine_request_handler(dock_message, vehicle)

    def process_docking_routine_finalize(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        dock_message = DockingRoutineMessage(**message["data"])
        if self.__docking_routine_finalize_handler and callable(
            self.__docking_routine_finalize_handler
        ):
            self.__docking_routine_finalize_handler(dock_message, vehicle)

    def process_task_v2(self, message: dict, vehicle: t.Optional[str] = None):
        """
        Load task to a Python object and pass it to task handler provided in the __init__
        method by implementers if applicable
        """
        task_data = message["data"]
        task = process_task_v2_message(task_data)
        if task.subtask_uuid and vehicle:
            vehicle_current_subtask = VehicleCurrentSubtask()
            vehicle_current_subtask[vehicle] = task.subtask_uuid

        if self.__task_v2_handler and callable(self.__task_v2_handler):
            self.__task_v2_handler(task, vehicle)

    def process_task_cancellation(self, message: dict, vehicle: t.Optional[str] = None):
        task_cancel = CancelTaskMessage(**message["data"])

        if self.__task_cancellation_handler and callable(
            self.__task_cancellation_handler
        ):
            self.__task_cancellation_handler(task_cancel, vehicle)

    def process_move(self, message: dict, vehicle: t.Optional[str] = None):
        move_message = MoveMessage(**message["data"])
        if self.__move_handler and callable(self.__move_handler):
            self.__move_handler(move_message, message, vehicle)

    def process_slow_down(self, message: dict, vehicle: t.Optional[str] = None):
        slow_down = SlowDownMessage(**message["data"])
        if self.__slow_down_handler and callable(self.__slow_down_handler):
            self.__slow_down_handler(slow_down, message, vehicle)

    def process_path_rerouting(self, message: dict, vehicle: t.Optional[str] = None):
        path_rerouting = PathReroutingMessage(**message)
        if self.__path_rerouting_handler and callable(self.__path_rerouting_handler):
            self.__path_rerouting_handler(path_rerouting, message, vehicle)

    def process_collision_clearance(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        collision_message = message["data"]
        clear_collision = process_clearance_data(collision_message)
        if self.__collision_clearance_handler and callable(
            self.__collision_clearance_handler
        ):
            self.__collision_clearance_handler(clear_collision, message, vehicle)

    def process_vehicle_initial_position_handler(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        initial_position = message["data"]
        if self.__vehicle_initial_position_handler and callable(
            self.__vehicle_initial_position_handler
        ):
            self.__vehicle_initial_position_handler(initial_position, message, vehicle)

    def process_request_for_topics(
        self, message: dict, vehicle: t.Optional[str] = None
    ):
        if self.__topic_list_handler and callable(self.__topic_list_handler):
            self.__topic_list_handler(message, vehicle)

    def process_topic_list(self, message: dict, vehicle: t.Optional[str] = None):
        topics = []

        for topic in message.get("data", []):
            topics.append(RosTopic(**topic))

        if self.__topic_list_initializer_handler and callable(
            self.__topic_list_initializer_handler
        ):
            self.__topic_list_initializer_handler(topics, message, vehicle)

    def process_message_error(self, message: dict):
        # Handle vehicle removal from fleet
        if message["errors"] and "vehicle" in message["errors"] and message["errors"]["vehicle"][0]:
            pattern = r"^Vehicle with UUID ([0-9a-fA-F]{32}) does not exist, or was removed from the fleet setup$"
            match = re.search(pattern, message["errors"]["vehicle"][0])
            logger.warning(f"{message['errors']['vehicle'][0]}")
            if match:
                logger.warning("Vehicle removal from fleet detected.")
                vehicle_to_remove_uuid = match.group(
                    1
                )  # Get the UUID from the error message
                self.process_remove_vehicle_from_fleet(vehicle_to_remove_uuid)
                return

        logger.warning(
            f"Validation failed for message with the following errors: {message}"
        )

        if self.__message_error_handler:
            self.__message_error_handler(message["errors"])

    def process_remove_vehicle_from_fleet(self, vehicle_uuid: str):
        if self.__remove_vehicle_from_fleet_handler and callable(
            self.__remove_vehicle_from_fleet_handler
        ):
            self.__remove_vehicle_from_fleet_handler(vehicle_uuid)

    def _get_registration_message(self):
        return Message(
            event=constants.EVENT_CONNECT,
            vehicles=self._get_registration_vehicles(),
        )

    def _get_registration_vehicles(self):
        return self.vehicles

    @property
    def vehicles(self):
        return self.__vehicles

    def add_vehicle(self, vehicle):
        if vehicle in self.__vehicles:
            raise ValueError("Vehicle already exists")
        self.__vehicles.append(vehicle)

    @vehicles.setter
    def vehicles(self, vehicles):
        if len(vehicles) != len(set(vehicles)):
            raise ValueError("There are duplicate vehicles")
        self.__vehicles = vehicles

    def remove_vehicle(self, vehicle):
        self.__vehicles.remove(vehicle)

    def close_ws(self):
        print("[MEILI_SDK] Force the Closing of WS")
        self.__connection.close()
