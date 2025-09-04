EVENT_DOCKING_ROUTINE = "docking_routine"
EVENT_CONNECT = "connect"
EVENT_LOCATION = "location"
EVENT_SPEED = "speed"
EVENT_BATTERY = "batteryStatus"
EVENT_GOAL_STATUS = "goalStatus"
EVENT_NOTIFICATION = "notification"
EVENT_TOPICS_LIST = "topics"
EVENT_TOPIC_DATA = "topic_data"
EVENT_PATH_DATA = "path_data"
EVENT_STATE = "state"
EVENT_MAP_UPDATE = "map_update"
EVENT_NEW_MISSION = "new_mission"
EVENT_VEHICLE_LOADSET_DATA = "loads"

ALL = (
    EVENT_DOCKING_ROUTINE,
    EVENT_CONNECT,
    EVENT_LOCATION,
    EVENT_SPEED,
    EVENT_BATTERY,
    EVENT_GOAL_STATUS,
    EVENT_NOTIFICATION,
    EVENT_TOPIC_DATA,
    EVENT_TOPICS_LIST,
    EVENT_PATH_DATA,
    EVENT_STATE,
    EVENT_MAP_UPDATE,
    EVENT_NEW_MISSION,
    EVENT_VEHICLE_LOADSET_DATA,
)

# Incoming actions
ACTION_DOCKING_ROUTINE_REQUEST = "docking_routine_request"
ACTION_DOCKING_ROUTINE_FINALIZE = "docking_routine_finalize_request"
ACTION_TASK_V2 = "taskv2"
ACTION_TASK_CANCELLATION = "cancelOrder"
ACTION_MOVE = "move"
ACTION_MOVE_TO_CHARGING_POINT = "move_charge"
ACTION_SLOW_DOWN = "slow_down"
ACTION_TOPIC_LIST = "request_topics"
ACTION_TOPIC_INITIALIZATION = "topic_init"
ACTION_ERROR = "errors"
ACTION_PATH_REROUTING = "path_rerouting"
ACTION_COLLISION_CLEARANCE = "clear_collision"
ACTION_UPDATE_MAP = "update_maps"
ACTION_UPDATE_VEHICLE_SETTINGS = "vehicle_settings"
ACTION_PAUSE_TASK = "startPause"
ACTION_RESUME_TASK = "stopPause"
ACTION_SET_INITIAL_POSITION = "set_initial_pose"
ACTION_UPDATE_MAP_ID = "update_map_id"

ALL_ACTIONS = (
    ACTION_DOCKING_ROUTINE_REQUEST,
    ACTION_DOCKING_ROUTINE_FINALIZE,
    ACTION_TASK_V2,
    ACTION_MOVE,
    ACTION_MOVE_TO_CHARGING_POINT,
    ACTION_SLOW_DOWN,
    ACTION_PATH_REROUTING,
    ACTION_TOPIC_LIST,
    ACTION_TOPIC_INITIALIZATION,
    ACTION_ERROR,
    ACTION_UPDATE_MAP,
    ACTION_UPDATE_VEHICLE_SETTINGS,
    ACTION_PAUSE_TASK,
    ACTION_RESUME_TASK,
    ACTION_SET_INITIAL_POSITION,
    ACTION_UPDATE_MAP_ID,
)

IGNORED_TYPES = (
    "initialized",
    "not_initialized",
)


class MapUpdateMessageStatuses:
    UPDATE = "update"
    CONFIRM = "confirm"


class FleetConsumerCodes:
    VERSION_INCOMPATIBLE = 4000
    INVALID_EVENT = 4001
    INVALID_TEAM = 4002
    INVALID_SITE = 4003

    ALL = (
        VERSION_INCOMPATIBLE,
        INVALID_EVENT,
        INVALID_TEAM,
        INVALID_SITE,
    )
    TEXT = {
        VERSION_INCOMPATIBLE: "Websocket version is incompatible with the server. "
        "Please update the meili-sdk library to the latest version.",
        INVALID_EVENT: "Invalid event type received from the server.",
        INVALID_TEAM: "Invalid team ID received from the server.",
        INVALID_SITE: "Invalid site ID received from the server.",
    }
