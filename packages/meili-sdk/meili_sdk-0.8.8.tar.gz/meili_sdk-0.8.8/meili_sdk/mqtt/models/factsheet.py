import typing as t
from datetime import datetime

from meili_sdk.exceptions import ValidationError
from meili_sdk.models.base import BaseModel
from meili_sdk.version import VERSION
from enum import Enum

__all__ = (
    "VDA5050VehiclePosition",
    "VDA5050NodePosition",
    "VDA5050VehicleBatteryState",
    "VDA5050NodeState",
    "VDA5050StateMessage",
)


CURRENT_HEADER_ID = 0

class VDA5050TypeSpecification(BaseModel):
    SeriesName: str
    SeriesDescription: str
    AgvKinematics: str
    AgvClass: str
    MaxLoadMass: float
    LocalizationTypes: t.List[str]
    NavigationTypes: t.List[str]
    
class VDA5050PhysicalParameters(BaseModel):
    SpeedMin: float
    SpeedMax: float
    AccelerationMax: float
    DecelerationMax: float
    HeightMin: float
    HeightMax: float
    Width: float
    Length: float
        
class VDA5050ProtocolLimits(BaseModel):
    VDA5050ProtocolLimits: t.List[str]
    
class VDA5050ParameterSupport(Enum):
    SUPPORTED = "SUPPORTED"
    REQUIRED = "REQUIRED"

class VDA5050OptionalParameters(BaseModel):
    Parameter: str
    Support: VDA5050ParameterSupport
    Description: str


class VDA5050ActionScopes(Enum):
    INSTANT = "INSTANT"
    NODE = "NODE"
    EDGE = "EDGE"
    
class VDA5050ValueDataType(Enum):
    BOOL = "BOOL" 
    NUMBER = "NUMBER"
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    STRING = "STRING"
    OBJECT = "OBJECT"
    ARRAY = "ARRAY"
    
class VDA5050ActionParameters(BaseModel):
    Key : str
    ValueDataType: VDA5050ValueDataType
    Description: str
    IsOptional: bool
    
class VDA5050AgvActions(BaseModel):
    ActionType: str
    ActionDescription: str
    ActionScopes: t.List[VDA5050ActionScopes]
    ActionParameters: t.List[VDA5050ActionParameters]
    ResultDescription: str
    
class VDA5050ProtocolFeatures(BaseModel):
    OptionalParameters: t.List[VDA5050OptionalParameters]
    AgvActions: t.List[VDA5050AgvActions]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
class VDA5050WheelType(Enum):
    DRIVE = "DRIVE"
    CASTER = "CASTER"
    FIXED = "FIXED"
    MECANUM = "MECANUM"
    
class VDA5050WheelPosition(BaseModel):
    X: float
    Y: float
    Theta: float

class VDA5050WheelDefinition(BaseModel):
    Type: VDA5050WheelType
    IsActiveDriven: bool
    IsActiveSteered: bool
    Position: VDA5050WheelPosition
    Diameter: float
    Width: float
    CenterDisplacement: float
    Constraints: str
    

class VDA5050FactsheetMessage(BaseModel):
    """
    Message to be sent to FMS MQTT Broker

    When initializing the message, headerId and timestamp will be automatically generated
    """

    headerId: int
    timestamp: datetime
    version: str
    manufacturer: str
    serialNumber: str
    typeSpecification: t.Optional[VDA5050TypeSpecification] = None
    physicalParameters: t.Optional[VDA5050PhysicalParameters] = None
    protocolLimits: t.Optional[VDA5050ProtocolLimits] = None
    protocolFeatures: t.Optional[VDA5050ProtocolFeatures] = None
    agvGeometry: t.Optional[t.List[VDA5050WheelDefinition]] = None
    loadSpecification: t.Optional[t.List[str]] = None
    localizationParameters: t.Optional[t.List[str]] = None
   
    def __init__(self, **kwargs):
        global CURRENT_HEADER_ID
        CURRENT_HEADER_ID += 1

        kwargs.setdefault("headerId", CURRENT_HEADER_ID)
        kwargs.setdefault("timestamp", datetime.now())

        super().__init__(**kwargs)



