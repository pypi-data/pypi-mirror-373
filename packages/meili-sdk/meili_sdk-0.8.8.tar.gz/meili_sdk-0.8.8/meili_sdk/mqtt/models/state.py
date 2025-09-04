import typing as t
from datetime import datetime

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel
from meili_sdk.version import VERSION

__all__ = (
    "VDA5050VehiclePosition",
    "VDA5050NodePosition",
    "VDA5050VehicleBatteryState",
    "VDA5050NodeState",
    "VDA5050StateMessage",
)


CURRENT_HEADER_ID = 0


class VDA5050VehiclePosition(BaseModel):
    x: float
    y: float
    positionInitialized: bool
    theta: float
    mapId: str
    mapDescription: t.Optional[str] = None
    localizationScore: t.Optional[float] = None
    deviationRange: t.Optional[float] = None

    def __init__(self, **kwargs):
        kwargs.setdefault("positionInitialized", True)
        super().__init__(**kwargs)

    def validate_theta(self):
        if self.theta < 0 or self.theta > 360:
            raise ValidationError("Theta must be between 0 and 360 degrees")


class VDA5050NodePosition(BaseModel):
    x: float
    y: float
    theta: float

    def validate_theta(self):
        if self.theta < 0 or self.theta > 360:
            raise ValidationError("Theta must be between 0 and 360 degrees")


class VDA5050VehicleBatteryState(BaseModel):
    batteryCharge: float
    batteryVoltage: t.Optional[float] = None
    batteryHealth: t.Optional[int] = None
    charging: bool
    reach: t.Optional[float] = None

    def __init__(self, **kwargs):
        kwargs.setdefault("charging", False)
        super().__init__(**kwargs)


class VDA5050NodeState(BaseModel):
    nodeId: str
    sequenceId: str
    nodeDescription: t.Optional[str] = None
    nodePosition: t.Optional[VDA5050NodePosition] = None
    released: bool

    def __init__(self, **kwargs):
        kwargs.setdefault("released", False)
        node_position = kwargs.pop("nodePosition")
        if not isinstance(node_position, VDA5050NodePosition):
            node_position = VDA5050NodePosition(**node_position)
        kwargs["nodePosition"] = node_position
        super().__init__(**kwargs)

class VDA5050ActionState(BaseModel):
    actionId: str
    actionType: t.Optional[str] = None
    actionStatus: str
    actionDescription: t.Optional[str] = None
    resultDescription: t.Optional[str] = None

    def validate_actionStatus(self):
        if self.actionStatus not in ["WAITING", "INITIALIZING", 
                                 "RUNNING", "FINISHED", "FAILED"
                                 ]:
            raise ValidationError("""actionStatus must be one of the following: [
                            "WAITING",
                            "INITIALIZING",
                            "RUNNING",
                            "FINISHED",
                            "FAILED"
                        ]""")
class VDA5050Trajectory(BaseModel):
    degree: float
    knotVector: t.List[float]
    controlPoints: t.List[t.List[float]]
        
class VDA5050EdgeState(BaseModel):
    edgeId: str
    sequenceId: str
    edgeDescription: t.Optional[str] = None
    released: bool
    trajectory: t.Optional[t.List[VDA5050Trajectory]] = None

class VDA5050ErrorReference(BaseModel):
    referenceKey: str
    referenceValue: str

class VDA5050Error(BaseModel):
    errorType: str
    errorLevel: str
    errorReferences: t.Optional[t.List[VDA5050ErrorReference]] = None
    errorDescription: t.Optional[str] = None

    def validatea_errorLevel(self):
        if self.errorLevel not in ["WARNING", "FATAL"]:
            raise ValidationError("""errorLevel must be one of "WARNING" or "FATAL" """)
        
class VDA5050Velocity(BaseModel):
    vx: float
    vy: float
    omega: float

class VDA5050SafetyState(BaseModel):
    eStop: str
    fieldViolation: bool
    
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("fieldViolation", False)
        super().__init__(**kwargs)
    
    def validate_eStop(self):
        if self.eStop not in ["AUTOACK", "MANUAL", "REMOTE", "NONE"]:
            raise ValidationError("""eStop must be one of the following: ["AUTOACK", "MANUAL", "REMOTE", "NONE"]""")
        
class VDA5050Information(BaseModel):
    infoType: str
    infoReferences: t.Optional[t.List[VDA5050ErrorReference]] = None
    infoDescription: t.Optional[str] = None
    infoLevel: str

    def validate_infoLevel(self):
        if self.infoLevel not in ["INFO", "DEBUG"]:
            raise ValidationError("""infoLevel must be one of the following: ["INFO", "DEBUG"]""")

class VDA5050LoadDimensions(BaseModel):
    length: float
    width: float
    height: t.Optional[float] = None

class VDA5050BoundingBoxReference(BaseModel):
    x: float
    y: float
    z: float
    theta: t.Optional[float] = None

class VDA5050Loads(BaseModel):
    loadId: str
    loadType: str
    loadPosition: str
    loadDimensions: VDA5050LoadDimensions
    boundingBoxReference: VDA5050BoundingBoxReference
    weight: float

class VDA5050StateMessage(BaseModel):
    """
    Message to be sent to FMS MQTT Broker

    When initializing the message, headerId and timestamp will be automatically generated
    """

    headerId: int
    timestamp: datetime
    version: str
    manufacturer: str
    serialNumber: str
    orderId: t.Optional[str] = ""
    orderUpdateId: t.Optional[str] = 0
    zoneSetId: t.Optional[str] = None
    lastNodeId: t.Optional[str] = None
    lastNodeSequenceId: t.Optional[int] = None
    driving: bool
    paused: bool
    newBaseRequest: t.Optional[bool] = None
    distanceSinceLastNode: t.Optional[float] = None
    nodeStates: t.Optional[t.List[VDA5050NodeState]] = None
    edgeStates: t.Optional[t.List[VDA5050EdgeState]] = None
    agvPosition: t.Optional[VDA5050VehiclePosition] = None
    batteryState: t.Optional[VDA5050VehicleBatteryState] = None
    operatingMode: str
    velocity: t.Optional[VDA5050Velocity] = None
    actionStates: t.Optional[t.List[VDA5050ActionState]] = None
    errors: t.Optional[t.List[VDA5050Error]] = None
    safetyState: t.Optional[t.List[VDA5050SafetyState]] = None
    information: t.Optional[t.List[VDA5050Information]] = None
    loads: t.Optional[t.List[VDA5050Loads]] = None

    def __init__(self, **kwargs):
        global CURRENT_HEADER_ID
        CURRENT_HEADER_ID += 1

        kwargs.setdefault("headerId", CURRENT_HEADER_ID)
        kwargs.setdefault("timestamp", datetime.now()) #.strftime("%Y-%m-%d %H:%M:%S.%f"))
        kwargs.setdefault("driving", False)
        kwargs.setdefault("paused", False)
        kwargs.setdefault("newBaseRequested", False)
        kwargs.setdefault("version", VERSION)
        kwargs.setdefault("operatingMode", "AUTOMATIC")

        node_states = kwargs.pop("nodeStates", None)
        node_state_objects = []

        if node_states:
            for node_state in node_states:
                if isinstance(node_state, VDA5050NodeState):
                    node_state_objects.append(node_state)
                else:
                    node_state_objects.append(VDA5050NodeState(**node_state))
            kwargs["nodeStates"] = node_state_objects

        if "agvPosition" in kwargs:
            agv_position = kwargs["agvPosition"]
            if not isinstance(agv_position, VDA5050VehiclePosition):
                kwargs["agvPosition"] = VDA5050VehiclePosition(**agv_position)

        if "batteryState" in kwargs:
            battery_state = kwargs["batteryState"]
            if not isinstance(battery_state, VDA5050VehicleBatteryState):
                kwargs["batteryState"] = VDA5050VehicleBatteryState(**battery_state)

        super().__init__(**kwargs)
