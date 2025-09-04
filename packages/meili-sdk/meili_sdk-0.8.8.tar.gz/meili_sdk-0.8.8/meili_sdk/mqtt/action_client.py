import typing as t

from paho.mqtt.client import Client as _Client

from meili_sdk.mqtt.client import MeiliMqttClient
from meili_sdk.mqtt.models import VDA5050ActionMessage, VDA5050OrderMessage


class MeiliMqttActionClient(MeiliMqttClient):
    """
    Extension of basic MeiliMqttClient

    It adds extra on_action and action_handler methods for handling actions coming
    from the FMS. It will automatically parse data to be presentable
    """

    __action_handler = None
    __order_handler = None

    def on_message(
        self,
        client: _Client,
        topic: str,
        raw_data: bytes,
        data: t.Optional[dict] = None,
    ):
        if topic.endswith("/actions") and data:
            self.on_action(VDA5050ActionMessage(**data))
        elif topic.endswith("/orders") and data:
            self.on_order(VDA5050OrderMessage(**data))
        else:
            super().on_message(client, topic, raw_data, data)

    def on_action(self, action: VDA5050ActionMessage):
        if self.action_handler:
            self.action_handler(action)

    def on_order(self, actions: VDA5050OrderMessage):
        if self.order_handler:
            return self.order_handler

    @property
    def action_handler(self) -> callable:
        return self.__action_handler

    @action_handler.setter
    def action_handler(self, handler: callable):
        if not callable(handler):
            raise TypeError("Handler must be of callable type")
        self.__action_handler = handler

    @property
    def order_handler(self) -> callable:
        return self.__order_handler

    @order_handler.setter
    def order_handler(self, handler: callable):
        if not callable(handler):
            raise TypeError("Handler must be of callable type")
        self.__order_handler = handler
