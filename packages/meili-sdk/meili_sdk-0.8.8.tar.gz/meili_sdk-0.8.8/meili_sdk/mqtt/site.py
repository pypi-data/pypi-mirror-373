import urllib.parse

from meili_sdk.site import get_host as _get_host


def get_host():
    """
    The same as meili_sdk.site.get_host but maps the application to correct MQTT URI
    and returns with MQTT scheme
    """
    host = _get_host()

    mapping = {
        "app": "mqtt",
        "stage": "mqtt-stage",
        "demo": "mqtt-demo",
        "development": "mqtt-development",
    }

    parsed = urllib.parse.urlparse(host)
    hostname = parsed.hostname

    try:
        app_name = hostname.split(".")[0]
        return f"mqtt://{mapping[app_name]}.meilirobots.com"
    except (IndexError, KeyError):
        return "mqtt://mqtt.meilirobots.com"
