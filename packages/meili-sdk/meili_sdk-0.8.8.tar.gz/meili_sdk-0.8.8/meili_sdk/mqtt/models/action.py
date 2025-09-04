import sys
import typing as t

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict
from meili_sdk.exceptions import MissingAttributesException
from meili_sdk.models.base import BaseModel


class ActionParameterType(TypedDict):
    key: str
    value: t.Any


class VDA5050Action(BaseModel):
    actionType: str
    actionParameters: t.List[ActionParameterType]

    def get_parameter(
        self, parameter: str
    ) -> t.Optional[t.Union[t.Iterable[ActionParameterType], ActionParameterType]]:
        parameters = list(
            filter(lambda x: x["key"] == parameter, self.actionParameters)
        )
        if len(parameters) == 1:
            return parameters[0]
        return parameters


class VDA5050ActionMessage(BaseModel):
    headerId: int
    version: str
    actions: t.List[VDA5050Action]

    def __init__(self, **kwargs):
        actions = kwargs.pop("actions", None)

        if not actions:
            raise MissingAttributesException(self.__class__, ["actions"])

        action_objs = []
        for action in actions:
            action_objs.append(VDA5050Action(**action))

        kwargs["actions"] = action_objs
        super().__init__(**kwargs)
