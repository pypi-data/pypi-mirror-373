import json
from types import TracebackType
from typing import Any, Callable, Generic, Type, TypeVar, cast

from enpi_api.l2.client.api.whoami_api import WhoamiApi
from enpi_api.l2.types.event import Event
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.types.whoami import Whoami
from enpi_api.l2.util.client import get_client
from enpi_api.l2.util.env import get_api_key_or_error, get_event_host, get_event_port
from loguru import logger
from paho.mqtt.client import Client, ConnectFlags, MQTTMessage
from paho.mqtt.enums import CallbackAPIVersion
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCode

E = TypeVar("E", bound=Event)

OnEventCallback = Callable[[str, E], None]
"""Callback function to be called when an event is received.

Args:
    topic (str): The topic on which the event was received.
    event (Event): The event that was received.
"""


# Function hidden from the user, should not be used directly by consumers of the SDK
def _create_paho_client(client_id: str, topic: str | list[str], on_event: OnEventCallback[E], event_type: Type[E]) -> Client:
    logger.debug(f"Listening for events on topic {topic} with client_id {client_id}")

    paho_client = Client(
        client_id=client_id,
        transport="websockets",
        clean_session=False,
        callback_api_version=CallbackAPIVersion.VERSION2,  # Editor says unexpected argument, not true
    )
    paho_client.ws_set_options(headers={"enpi-api-key": get_api_key_or_error()}, path="/events")

    # If we are not localhost, we need to call `tls_set`
    if "localhost" not in get_event_host():
        paho_client.tls_set()

    def on_connect(client: Client, _userdata: Any, _connect_flags: ConnectFlags, _reason_code: ReasonCode, _properties: Properties | None = None) -> None:  # type: ignore[misc]
        logger.info("Connected to events endpoint")
        if isinstance(topic, list):
            topics = [(t, 1) for t in topic]
            client.subscribe(topics, qos=1)
        else:
            client.subscribe(topic, qos=1)

    def on_subscribe(_client: Client, _userdata: Any, _mid: int, reason_code_list: list[ReasonCode], _properties: Properties | None = None) -> None:  # type: ignore[misc]
        logger.info(f"Subscribed to topic with QoS {reason_code_list[0]}")

    def on_message(_client: Client, _userdata: Any, message: MQTTMessage) -> None:  # type: ignore[misc]
        # In our case, payload is always a JSON string
        json_payload = json.loads(message.payload.decode("utf-8"))
        # Parse it as our event type
        try:
            event = event_type.model_validate(json_payload)
            on_event(message.topic, event)
        except Exception as e:
            logger.error(f"Failed to parse event: {json.dumps(json_payload)}, not calling callback") if event_type is Event else None
            logger.error(f"Error: {e}")

    def on_connect_fail(_client: Client, _userdata: Any) -> None:  # type: ignore[misc]
        # This is also logged when the connection is lost, and it's trying to re-connect.
        logger.warning("Connection failed, retrying...")

    paho_client.on_connect = on_connect
    paho_client.on_message = on_message
    paho_client.on_connect_fail = on_connect_fail
    paho_client.on_subscribe = on_subscribe

    return paho_client


class EventListener(Generic[E]):
    """Base event listener class, handles the context managing and client creation.

    **Do not use this class directly, use `UserEventListener`, `SpaceEventListener` or `OrganizationEventListener` instead.**
    """

    _paho_client: Client

    def __init__(self, on_event: OnEventCallback[E], client_id: str, topic: str | list[str], event_type: Type[E] = cast(Type[E], Event)) -> None:
        if type(self) is EventListener:
            raise TypeError("EventListener should not be used directly, use UserEventListener or OrganizationEventListener")

        self.event_type = event_type
        self._paho_client = _create_paho_client(client_id, topic, on_event, event_type)

    def _connect(self) -> None:
        logger.debug("Connecting to events endpoint")

        host = get_event_host()
        port = get_event_port()

        logger.debug(f"Event host: {host}")
        logger.debug(f"Event port: {port}")

        self._paho_client.connect(host, port, 60)

    def __enter__(self) -> None:
        self._connect()
        self._paho_client.loop_start()

    def __exit__(self, exc_type: Type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None) -> None:
        logger.debug("Disconnecting from events endpoint")
        self._paho_client.loop_stop()

    def whoami(self) -> Whoami:
        api_client = get_client()
        whoami_api = WhoamiApi(api_client, log_level=LogLevel.Info)
        return whoami_api.whoami()

    def loop_forever(self) -> None:
        """Start listening for events indefinitely. This will block the main thread."""

        self._connect()

        logger.debug("Listening for events indefinitely")
        self._paho_client.loop_forever()

    def start_listening(self) -> None:
        logger.info("Starting EventListener loop")
        self._connect()
        self._paho_client.loop_start()

    def stop_listening(self) -> None:
        logger.info("Stopping EventListener loop")
        self._paho_client.loop_stop()
