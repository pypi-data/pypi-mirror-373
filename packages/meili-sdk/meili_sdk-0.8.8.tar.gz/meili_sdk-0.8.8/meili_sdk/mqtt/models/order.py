import typing as t

from meili_sdk.exceptions import MissingAttributesException
from meili_sdk.models.base import BaseModel
from meili_sdk.version import VERSION

CURRENT_HEADER_ID = 0


class VDA5050ControlPoint(BaseModel):
    x: float
    y: float


class VDA5050Trajectory(BaseModel):
    controlPoints: t.Optional[t.List[VDA5050ControlPoint]] = None

    def __init__(self, **kwargs):
        if "controlPoints" in kwargs:
            control_points = kwargs["controlPoints"]
            cp_objs = []

            for cp in control_points:
                if isinstance(cp, VDA5050ControlPoint):
                    cp_objs.append(cp)
                else:
                    cp_objs.append(VDA5050ControlPoint(**cp))
            kwargs["control_points"] = cp_objs

        super().__init__(**kwargs)


class VDA5050NodePosition(BaseModel):
    x: float
    y: float
    theta: float
    allowedDeviationXY: float
    allowedDeviationTheta: float

    def __init__(self, **kwargs):
        kwargs.setdefault("allowedDeviationXY", 0.1)
        kwargs.setdefault("allowedDeviationTheta", 1)
        super().__init__(**kwargs)


class VDA5050Node(BaseModel):
    nodeId: str
    sequenceId: str
    description: t.Optional[str] = None
    released: bool
    nodePosition: VDA5050NodePosition

    def __init__(self, **kwargs):
        kwargs.setdefault("released", False)

        try:
            position = kwargs["nodePosition"]
        except KeyError:
            raise MissingAttributesException(self.__class__, "nodePosition")

        if not isinstance(position, VDA5050NodePosition):
            kwargs["nodePosition"] = VDA5050NodePosition(**position)
        super().__init__(**kwargs)


class VDA5050Edge(BaseModel):
    edgeId: t.Optional[int] = None
    sequenceId: int
    released: bool
    endNodeId: str
    trajectory: t.Optional[VDA5050Trajectory] = None

    def __init__(self, **kwargs):
        kwargs.setdefault("released", False)
        if "trajectory" in kwargs:
            if not isinstance(kwargs["trajectory"], VDA5050Trajectory):
                kwargs["trajectory"] = VDA5050Trajectory(**kwargs["trajectory"])

        super().__init__(**kwargs)


class VDA5050OrderMessage(BaseModel):
    headerId: int
    version: str
    manufacturer: str
    serialNumber: str
    orderId: str
    orderUpdateId: t.Optional[str] = None
    nodes: t.Optional[t.List[VDA5050Node]] = None
    edges: t.Optional[t.List[VDA5050Edge]] = None

    def __init__(self, **kwargs):
        global CURRENT_HEADER_ID
        CURRENT_HEADER_ID += 1

        kwargs.setdefault("headerId", CURRENT_HEADER_ID)
        kwargs.setdefault("version", VERSION)

        if "nodes" in kwargs:
            nodes = kwargs["nodes"]
            node_objs = []

            for node in nodes:
                if isinstance(node, VDA5050Node):
                    node_objs.append(node)
                else:
                    node_objs.append(VDA5050Node(**node))

            kwargs["nodes"] = node_objs

        if "edges" in kwargs:
            edges = kwargs["edges"]
            edge_objs = []

            for edge in edges:
                if isinstance(edge, VDA5050Edge):
                    edge_objs.append(edge)
                else:
                    edge_objs.append(VDA5050Edge(**edge))

            kwargs["edges"] = edge_objs

        super().__init__(**kwargs)
