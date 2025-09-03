import uuid
from typing import Callable

from enpi_api.l1.openapi_client.api_client import ApiClient
from enpi_api.l2.client.api.whoami_api import WhoamiApi
from enpi_api.l2.events.base_event_listener import EventListener
from enpi_api.l2.types.event import Event
from enpi_api.l2.types.log import LogLevel
from enpi_api.l2.util.env import get_event_root_topic
from loguru import logger

OnEventCallback = Callable[[str, Event], None]


class TaskEventListener(EventListener[Event]):
    def __init__(self, on_event: OnEventCallback, api_client: ApiClient, client_id: str | None = None):
        whoami_api = WhoamiApi(api_client, log_level=LogLevel.Info)
        whoami = whoami_api.whoami()
        user_id = whoami.user.id

        client_id = client_id or str(uuid.uuid4())
        client_id = f"{get_event_root_topic()}/{user_id}/{client_id}"
        topics = [f"{get_event_root_topic()}/space/{s.id}" for s in whoami.spaces]

        super().__init__(on_event, client_id, topics, Event)

    def start_listening(self) -> None:
        logger.info("Starting TaskEventListener loop")
        self._connect()
        self._paho_client.loop_start()

    def stop_listening(self) -> None:
        logger.info("Stopping TaskEventListener loop")
        self._paho_client.loop_stop()
