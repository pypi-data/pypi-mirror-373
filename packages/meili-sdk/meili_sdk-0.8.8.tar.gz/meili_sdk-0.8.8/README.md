# Meili FMS SDK library

Official Meili FMS SDK library.

## Status:

[![pipeline status](https://gitlab.com/meilirobots/dev/meili-sdk/badges/master/pipeline.svg)](https://gitlab.com/meilirobots/dev/meili-sdk/-/commits/release)

[![coverage report](https://gitlab.com/meilirobots/dev/meili-sdk/badges/master/coverage.svg)](https://gitlab.com/meilirobots/dev/meili-sdk/-/commits/release)


## Installation

```shell
pip install meili-sdk

# or with MQTT support

pip install "meili-sdk[MQTT]"

# or from local repo - for development

python3 -m pip install -e .
```

## Intro

This library aims to make it easier for 3rd party developers to integrate with
Meili FMS via API or Websockets.

## Prerequisites

To start using the SDK you will need either one of the API Tokens or Fleet Token
to connect via REST or WS.

## Getting started

### Using different sites

By default, all the traffic goes to `app.meilirobots.com`, but you can override it in one of these ways:

- Pass `override_host` kwarg to `get_client` or client classes
- Set `MEILI_HOST` env variable
- Set `site` in `~/.meili/cfg.yaml`

### RESTful

We provide a magic method to evaluate the token and return the correct type
of API client for you. See the snipped below on how to use it:

```python
from meili_sdk.clients import get_client

client = get_client("my-token")
```

If token will not be able to evaluate it will return a default `APITokenClient`.

#### Accessing resources

Each API client provides 4 methods that will return resource access:

```
.get_user_resources()
.get_team_resources()
.get_organization_resources()
.get_vehicle_resources()
```

Note that not all resources are accessible through all clients and might raise
`NotImplemented` exception.

#### Using models

Since we are a Django workshop, we like to do things in such way and therefore our models 
are also written similarly.

All models can have `.validate_{field_name}(value)` functions that will be automatically 
called when running `.validate()`.

If any of the values are not passed to constructors that are defined on the class without
defaults, a `MissingAttributesException` exception will be risen.

### Websockets

If your application requires asynchronous connection, you can use `MeiliWebsocketClient` to do so.

We have written our client in such way that you will receive already constructed objects from it
and will not have to worry about parsing and validating data.

Here is an example use of our websocket client:

```python
from meili_sdk.websockets.client import MeiliWebsocketClient


def open_handler():
    print("WS opened")


def close_handler():
    print("WS CLOSED")


def error_handler(*_):
    print("error has occurred")


client = MeiliWebsocketClient(
    "77b971e8f47e421045d384558059c31679b4b6ca",
    open_handler=open_handler,
    close_handler=close_handler,
    error_handler=error_handler,
)

client.add_vehicle("2eb03045cbc640fdbd2181ab60387b7a")
client.run()
```

If you want to run it without block the program flow, you can run it inside a thread
using `.run_in_thread()` method.

Here are all the parameters you can pass to the constructor of websocket client:

```
token (str) - authentication token with the WS
fleet (bool) - use fleet websocket if set to true (default: true)
open_handler() (callable) - a callable object that will be called with no parameters when websocket is opened
close_handler() (callable) - a callable objects that will be called with no parameters when websocket is closed
error_handler(err) (callable) - a callable with a single parameter that will receive the exception as a parameter
task_handler(task: Task, data: dict, vehicle: str) - a callable that will be called when a new task is received
move_action_handler(message: MoveMessage, data: dict, vehicle: str) - a callable for moving vehicle according to FMS
slow_down_handler(message: SlowDownMessage, data: dict, vehicle: str) - a callable for altering movement of robots
topic_list_handler(data: dict, vehicle: str) - a callable for handling topic list request
topic_list_initializer_handler(topics: List[RosTopic], data: dict, vehicle: str) - a callable to initialize topics
```

### MQTT

```python
from meili_sdk.mqtt.client import MeiliMqttClient


def on_message(client, topic, raw_data, data):
    print(f"message in topic: {topic} received with the following data: {data}")


def on_open(*_):
    print(f"Connection was opened")


c = MeiliMqttClient(
    client_id="meili-agent-0f24942b-fce2-498b-b6fa-bcb995e8f377",
    host="ac8bf42345081496faead3a80186328e-349527337.eu-north-1.elb.amazonaws.com",
    port=1883,
    open_handler=on_open,
    message_handler=on_message,
)

c.run(block=False)
c.subscribe(
    "meili/setup/4c55eb782d104fa8bbdf4c3b912b959b/vehicle/5e5ee61798954bcb9dcd3b02735072ea/state"
)
```