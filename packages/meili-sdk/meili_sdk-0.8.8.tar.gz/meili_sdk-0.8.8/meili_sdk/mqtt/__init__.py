try:
    import paho as _

    from .action_client import MeiliMqttActionClient
    from .client import MeiliMqttClient
except ImportError as exc:
    from meili_sdk.exceptions import BadlyConfiguredException

    raise BadlyConfiguredException(
        msg="Paho is not installed. Try install the SDK "
        "using: pip install meili-sdk[MQTT] or install paho-mqtt "
        "separately"
    ) from exc
