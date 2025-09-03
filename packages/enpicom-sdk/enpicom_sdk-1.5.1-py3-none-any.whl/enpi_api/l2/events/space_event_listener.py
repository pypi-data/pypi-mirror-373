import uuid
from typing import Callable

from enpi_api.l2.events.base_event_listener import EventListener
from enpi_api.l2.types.event import Event
from enpi_api.l2.util.env import get_event_root_topic

OnEventCallback = Callable[[str, Event], None]


class SpaceEventListener(EventListener[Event]):
    def __init__(self, on_event: OnEventCallback, client_id: str | None = None):
        """Listen for events on the space level.

        The spaces that the events are listened for is determined by the API key used.

        This class is a context manager that listens for events on the space level. It will automatically
        subscribe to the correct topics and connect to the endpoint. When an event is received, the provided callback
        function is called with the topic and the event as arguments. When the context manager is exited, the connection
        will be closed automatically.
        When using this as a context manager, the connection will be spawned on a separate thread so the main thread is
        not blocked.

        Alternatively you can use the loop_forever method to keep the connection open indefinitely, keep in mind that
        this will block the main thread.

        Args:
            on_event (OnEventCallback): The callback function to be called when an event is received.
            client_id (str | None): The unique identifier of the client. Defaults to a random UUID. Take care when providing a
              custom client ID, as it must be unique across all clients listening for events. If another script uses
              the same client ID, the other will be disconnected. Defaults to a random UUID.

        Example:
            Using it as a context manager:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            with SpaceEventListener(on_event=on_event):
                while True:
                    pass
            ```

            Or using it with the `loop_forever` method, in this case, to stop the loop, the script must be interrupted:

            ```python
            def on_event(topic: str, event: Event):
                print(f"Received event: {event} on topic: {topic}")

            listener = SpaceEventListener(on_event=on_event)
            listener.loop_forever()
            ```
        """
        whoami = self.whoami()

        client_id = client_id or str(uuid.uuid4())
        client_id = f"{get_event_root_topic()}/{whoami.user.id}/{client_id}"
        topics = [f"{get_event_root_topic()}/space/{s.id}" for s in whoami.spaces]

        super().__init__(on_event, client_id, topics)
