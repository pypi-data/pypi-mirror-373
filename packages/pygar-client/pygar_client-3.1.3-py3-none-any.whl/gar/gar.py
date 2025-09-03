"""
GAR Client Module

See GARClient documentation for more details.
"""

import asyncio
import getpass
import logging
import os
import ssl
import threading
import time
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple, Union

import websockets
from msgspec import DecodeError, json
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed

import __main__


def our_enc_hook(obj: Any) -> Any:
    """ " Convert enum instances to their string names for JSON serialization."""
    if isinstance(obj, Enum):
        return obj.name

    # msgspec.json apparently checks for exact type, rather than isinstance
    # convert derived primitives so they don't format as json strings

    if isinstance(obj, float):
        return float(obj)

    if isinstance(obj, int):
        return int(obj)

    return str(obj)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-public-methods
class GARClient:
    """
    A client implementation for the Generic Active Records (GAR) protocol using WebSockets.

    See trsgar.py for example usage.

    The GARClient class provides a Python interface for connecting to a GAR server
    using WebSockets as the transport layer. It handles the protocol details including
    message serialization, heartbeat management, topic and key enumeration, record
    updates, and subscription management.

    The client maintains separate mappings for server-assigned and client-assigned
    topic and key IDs, allowing for independent enumeration on both sides. It provides
    methods for subscribing to data, publishing records, and registering handlers for
    various message types.

    Key features:
    - Automatic heartbeat management to maintain connection
    - Support for topic and key int <-> string introductions
    - Record creation, updating, and deletion
    - Subscription management with filtering options
    - Customizable message handlers for all protocol message types
    - Thread-safe message sending
    - Automatic reconnection on WebSocket connection loss

    See the full documentation at https://trinityriversystems.com/docs/ for detailed
    protocol specifications and usage instructions.
    """

    _initial_grace_period: bool
    _initial_grace_deadline: float

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        ws_endpoint: str,
        working_namespace: str | None = None,
        heartbeat_timeout_interval: int = 4000,
        allow_self_signed_certificate: bool = False,
        ws_buffer_size: int = 2097152,
    ) -> None:
        """
        Initialize the GAR (Generic Active Records) client.

        Creates a new GAR client instance that connects to a GAR server using WebSockets.
        It sets up internal data structures for tracking topics, keys, and message handlers,
        and initializes the heartbeat mechanism for maintaining the connection.

        Args:
            ws_endpoint: WebSocket endpoint string in the format "ws://address:port"
                         (e.g., "ws://localhost:8765") where the GAR server is listening.
            user: Client username string used for identification and authentication
                  with the server. This is included in the socket identity.
            heartbeat_timeout_interval: Timeout in milliseconds for checking heatbeats. Default is 4000ms (4 seconds).

        Returns:
            None

        Note:
            The client is not started automatically after initialization.
            Call the start() method to begin communication with the server.
            start() will run the IO loop until stop() is called.
            Use threading.Thread(target=gar_client.start) to run in the background.
        """
        self.ws_endpoint = ws_endpoint
        self.websocket: Optional[ClientConnection] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.connected = False
        self.encoder = json.Encoder(enc_hook=our_enc_hook)
        self.decoder = json.Decoder(float_hook=Decimal)
        self.reconnect_delay = 5.0  # Seconds to wait before reconnecting

        self.pid = os.getpid()
        self.logger = logging.getLogger(__name__)

        self.user = os.getenv("GAR_USERNAME") or os.environ.get(
            "USER", getpass.getuser()
        )
        self.application = os.path.basename(getattr(__main__, "__file__", "unknown-py"))
        self.working_namespace = working_namespace
        self.heartbeat_timeout_interval = heartbeat_timeout_interval
        self.version = 650706

        self._key_lock = threading.Lock()
        self._topic_lock = threading.Lock()

        self.clear_connection_state()

        self.running = False
        self.heartbeat_thread: Optional[threading.Thread] = None

        self.message_handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}

        self.last_heartbeat_time = time.time()

        self.heartbeat_timeout_callback: Optional[Callable[[], None]] = None
        self.stopped_callback: Optional[Callable[[], None]] = None

        self.allow_self_signed_certificate = allow_self_signed_certificate
        self.exit_code = 0

        logging.basicConfig(level=logging.INFO)
        self.register_default_handlers()

        # Asyncio event loop for WebSocket operations
        self.loop = asyncio.new_event_loop()

        self.active_subscription_group = 0

        self.ws_buffer_size = ws_buffer_size

    def clear_connection_state(self) -> None:
        """
        Reset all connection-related state:
        server/client topic/key mappings, counters, grace flags, and records.
        """
        with self._key_lock:
            with self._topic_lock:
                # Server assigned topic/key <-> name mappings
                self.server_topic_id_to_name: Dict[int, str] = {}
                self.server_topic_name_to_id: Dict[str, int] = {}
                self.server_key_id_to_name: Dict[int, str] = {}
                self.server_key_name_to_id: Dict[str, int] = {}

                # Client assigned topic/key counters and name <-> ID maps
                self.local_topic_counter = 1
                self.local_key_counter = 1
                self.local_topic_map: Dict[str, int] = {}
                self.local_key_map: Dict[str, int] = {}

                # Heartbeat grace period flags
                self._initial_grace_period = False
                self._initial_grace_deadline = 0.0

                # Cached records
                self.record_map: Dict[Tuple[int, int], Any] = {}

    async def connect(self) -> None:
        """Establish WebSocket connection with reconnection logic, using GAR subprotocol."""
        # Before attempting a new connection, clear any previous state
        self.clear_connection_state()

        while self.running and not self.connected:
            try:
                connect_kwargs: Dict[str, Any] = {"subprotocols": ["gar-protocol"]}
                if self.ws_endpoint.lower().startswith("wss://"):
                    ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                    if self.allow_self_signed_certificate:
                        ssl_ctx.check_hostname = False
                        ssl_ctx.verify_mode = ssl.CERT_NONE
                    connect_kwargs["ssl"] = ssl_ctx

                async with websockets.connect(
                    self.ws_endpoint, max_size=self.ws_buffer_size, **connect_kwargs
                ) as websocket:
                    self.websocket = websocket
                    self.connected = True
                    self.logger.info(
                        "Connected to WebSocket server at %s using gar-protocol",
                        self.ws_endpoint,
                    )
                    await asyncio.gather(
                        self._send_messages(), self._receive_messages()
                    )
            except (ConnectionClosed, ConnectionRefusedError):
                self.logger.exception(
                    "WebSocket connection to %s failed. Reconnecting in %s seconds...",
                    self.ws_endpoint,
                    self.reconnect_delay,
                )
                self.connected = False
                self.websocket = None
                await asyncio.sleep(self.reconnect_delay)

    async def _send_messages(self) -> None:
        """Send messages from the queue to the WebSocket server."""
        while self.connected and (self.running or not self.message_queue.empty()):
            try:
                message = await self.message_queue.get()
                if message is None:
                    break
                if self.websocket:
                    json_message = self.encoder.encode(message).decode()
                    await self.websocket.send(json_message)
                    # self.logger.debug("Sent: %s", json_message)
                self.message_queue.task_done()
            except ConnectionClosed:
                self.logger.warning("Connection closed while sending.")
                self.stop()
                break
            # pylint: disable=broad-exception-caught
        self.connected = False
        self.logger.info("Done sending messages.")

        # try to clear spurious "RuntimeWarning: coroutine 'Queue.put' was never awaited"
        try:
            self.message_queue.get_nowait()
        except asyncio.QueueEmpty:
            pass

    async def _receive_messages(self) -> None:
        """Receive and process messages from the WebSocket server."""
        while self.connected and self.running:
            try:
                if self.websocket:
                    message = await asyncio.wait_for(self.websocket.recv(), timeout=1)
                    msg = self.decoder.decode(message)
                    self._process_message(msg)
            except asyncio.TimeoutError:
                self.check_heartbeat()
            except ConnectionClosed:
                self.logger.info("Connection closed while receiving.")
                self.halt()
                break
            except DecodeError as e:
                self.logger.error("Invalid JSON received: %s", e)
                break
        self.stop()
        asyncio.run_coroutine_threadsafe(
            self.message_queue.put(None), self.loop
        )  # Put None into the queue to stop the send loop
        self.logger.info("Done receiving messages.")

    def register_handler(
        self,
        message_type: str,
        handler: Callable[[Dict[str, Any]], None],
        subscription_group: int = 0,
    ) -> None:
        """Register a callback handler for a specific message type."""
        self.message_handlers[
            (
                f"{message_type} {subscription_group}"
                if subscription_group
                else message_type
            )
        ] = handler

    def register_introduction_handler(
        self, handler: Callable[[int, int, str, Optional[str]], None]
    ) -> None:
        """Handler for Introduction: (version, heartbeat_timeout_interval, user, schema)"""

        def wrapper(msg: Dict[str, Any]):
            value = msg["value"]
            handler(
                value["version"],
                value["heartbeat_timeout_interval"],
                value["user"],
                value.get("schema"),
            )

        self.register_handler("Introduction", wrapper)

    def clear_introduction_handler(self) -> None:
        """Remove the registered introduction handler."""
        self.message_handlers.pop("Introduction", None)

    def register_heartbeat_handler(self, handler: Callable[[int], None]) -> None:
        """Handler for Heartbeat"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["u_milliseconds"])

        self.register_handler("Heartbeat", wrapper)

    def clear_heartbeat_handler(self) -> None:
        """Remove the registered heartbeat handler."""
        self.message_handlers.pop("Heartbeat", None)

    def register_logoff_handler(self, handler: Callable[[], None]) -> None:
        """Handler for Logoff: no arguments"""

        # pylint: disable=unused-argument
        def wrapper(msg: Dict[str, Any]):
            handler()

        self.register_handler("Logoff", wrapper)

    def clear_logoff_handler(self) -> None:
        """Remove the registered logoff handler."""
        self.message_handlers.pop("Logoff", None)

    def register_error_handler(self, handler: Callable[[str], None]) -> None:
        """Handler for Error: (message)"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["message"])

        self.register_handler("Error", wrapper)

    def clear_error_handler(self) -> None:
        """Remove the registered error handler."""
        self.message_handlers.pop("Error", None)

    def register_topic_introduction_handler(
        self, handler: Callable[[int, str], None]
    ) -> None:
        """Handler for TopicIntroduction: (topic_id, name)"""

        def wrapper(msg: Dict[str, Any]):
            value = msg["value"]
            handler(value["topic_id"], value["name"])

        self.register_handler("TopicIntroduction", wrapper)

    def clear_topic_introduction_handler(self) -> None:
        """Remove the registered topic introduction handler."""
        self.message_handlers.pop("TopicIntroduction", None)

    def register_key_introduction_handler(
        self,
        handler: Callable[[int, str, Optional[list[str]]], None],
        subscription_group: int = 0,
    ) -> None:
        """Handler for KeyIntroduction: (key_id, name, class_list)"""

        def wrapper(msg: Dict[str, Any]):
            value = msg["value"]
            handler(value["key_id"], value["name"], value.get("class_list"))

        self.register_handler("KeyIntroduction", wrapper, subscription_group)

    def register_delete_key_handler(
        self, handler: Callable[[int], None], subscription_group: int = 0
    ) -> None:
        """Handler for DeleteKey: (key_id)"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["key_id"])

        self.register_handler("DeleteKey", wrapper, subscription_group)

    def register_subscription_status_handler(
        self, handler: Callable[[str, str], None]
    ) -> None:
        """
        Handler for SubscriptionStatus: (name)
        Callback args are (name, status)
        status can be "Streaming" or "Finished"
        """

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["name"], msg["value"]["status"])

        self.register_handler("SubscriptionStatus", wrapper)

    def clear_subscription_status_handler(self) -> None:
        """Remove the registered subscription status handler."""
        self.message_handlers.pop("SubscriptionStatus", None)

    def register_delete_record_handler(
        self, handler: Callable[[int, int], None], subscription_group: int = 0
    ) -> None:
        """Handler for DeleteRecord: (key_id, topic_id)"""

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"]["key_id"], msg["value"]["topic_id"])

        self.register_handler("DeleteRecord", wrapper, subscription_group)

    def register_record_update_handler(
        self, handler: Callable[[int, int, Any], None], subscription_group: int = 0
    ) -> None:
        """Handler for JSONRecordUpdate: (key_id, topic_id, value)"""

        def wrapper(msg: Dict[str, Any]):
            record_id = msg["value"]["record_id"]
            handler(record_id["key_id"], record_id["topic_id"], msg["value"]["value"])

        self.register_handler("JSONRecordUpdate", wrapper, subscription_group)

    def register_batch_update_handler(
        self, handler: Callable[[dict, int], None], subscription_group: int = 0
    ) -> None:
        """
        Handler for BatchUpdate: (batch_data, subscription_group)
        If a batch handler is registered it is expected to process all the updates in the batch.
        If no batch handler is registered, individual key introductions and record updates will be fanned out to their respective handlers.
        """

        def wrapper(msg: Dict[str, Any]):
            handler(msg["value"], subscription_group)

        self.register_handler("BatchUpdate", wrapper, subscription_group)

    def register_heartbeat_timeout_handler(self, handler: Callable[[], None]) -> None:
        """Register a callback to handle heartbeat timeout events."""
        self.heartbeat_timeout_callback = handler

    def clear_heartbeat_timeout_handler(self) -> None:
        """Remove the registered heartbeat timeout handler."""
        self.heartbeat_timeout_callback = None

    def register_stopped_handler(self, handler: Callable[[], None]) -> None:
        """Register a callback to handle client stopped events."""
        self.stopped_callback = handler

    def clear_stopped_handler(self) -> None:
        """Remove the registered stopped handler."""
        self.stopped_callback = None

    def register_default_handlers(self) -> None:
        """Register default logging handlers for all message types."""
        self.register_introduction_handler(
            lambda version, interval, user, schema: self.logger.info(
                "Connected to server: %s", user
            )
        )
        self.register_heartbeat_handler(
            lambda ms: self.logger.debug("Heartbeat received %dms", ms)
        )
        self.register_logoff_handler(lambda: self.logger.info("Logoff received"))
        self.register_topic_introduction_handler(
            lambda topic_id, name: self.logger.info(
                "New server topic: %s (Server ID: %d)", name, topic_id
            )
        )
        self.register_key_introduction_handler(
            lambda key_id, name, class_list: self.logger.debug(
                "New server key: %s : %s (Server ID: %d)", name, class_list, key_id
            )
        )
        self.register_delete_key_handler(
            lambda key_id: self.logger.debug(
                "Delete key: %s (Server ID: %d)",
                self.server_key_id_to_name.get(key_id),
                key_id,
            )
        )
        self.register_subscription_status_handler(
            self._default_subscription_status_handler
        )
        self.register_delete_record_handler(
            lambda key_id, topic_id: self.logger.debug(
                "Delete record: %s - %s",
                self.server_key_id_to_name.get(key_id),
                self.server_topic_id_to_name.get(topic_id),
            )
        )
        self.register_record_update_handler(
            lambda key_id, topic_id, value: self.logger.debug(
                "Record update: %s - %s = %s",
                self.server_key_id_to_name.get(key_id),
                self.server_topic_id_to_name.get(topic_id),
                value,
            )
        )

    def _default_subscription_status_handler(self, name: str, status: str) -> None:
        """Default handler for subscription status messages."""
        self.logger.info("Subscription %s status: %s", name, status)
        if status == "NeedsContinue":
            self.logger.info(
                "Snapshot size limit reached, sending SubscribeContinue for %s", name
            )
            self.send_subscribe_continue(name)

    def start(self) -> None:
        """Start the client and send introduction message."""
        self.running = True
        intro_msg = {
            "message_type": "Introduction",
            "value": {
                "version": self.version,
                "pid": self.pid,
                "heartbeat_timeout_interval": self.heartbeat_timeout_interval,
                "user": self.user,
                "application": self.application,
                "working_namespace": self.working_namespace,
            },
        }
        self.logger.debug("Sending: %s", intro_msg)
        self.send_message(intro_msg)
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop, daemon=True
        )
        self.heartbeat_thread.start()
        # Run the WebSocket connection in the asyncio event loop
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())
        self.logger.info("GAR processing loop completed")
        self.loop.close()
        self.stop()
        if self.stopped_callback:
            self.stopped_callback()

    def stop(self) -> None:
        """
        Stop the client and terminate all client operations.
        Note this does not block until the connection is closed.
        Register a stopped callback to be notified when the control loop has stopped.
        """
        if self.running:
            self.logger.info("Stopping GAR client")

        self.running = False

    def halt(self) -> None:
        """
        Stops the client without sending any pending messages.
        """
        self.stop()
        self.connected = False

    def logoff(self) -> None:
        """Send a logoff message to the server and stop the client."""
        msg = {"message_type": "Logoff"}
        self.send_message(msg)
        self.logger.debug("Sending: %s", msg)
        self.stop()

    def __del__(self) -> None:
        """Clean up resources when the object is destroyed."""
        if self.loop and not self.loop.is_closed():
            self.loop.close()

    def send_message(self, message: Dict[str, Any]) -> None:
        """Send a JSON message through the WebSocket."""
        if self.running:
            asyncio.run_coroutine_threadsafe(self.message_queue.put(message), self.loop)
        else:
            self.logger.debug("Client is not running; message not sent %s", message)

    def _heartbeat_loop(self) -> None:
        """Send periodic heartbeat messages."""
        while self.running:
            msg = {
                "message_type": "Heartbeat",
                "value": {
                    "u_milliseconds": int(time.time() * 1000),
                },
            }
            self.logger.debug("Sending: %s", msg)
            self.send_message(msg)
            time.sleep(min(10, self.heartbeat_timeout_interval / 1000 / 2))

    def check_heartbeat(self) -> None:
        """Check if the heartbeat has timed out."""
        # Enforce heartbeat timeout, with 10× grace for the very first beat
        if self._initial_grace_period:
            cutoff = self._initial_grace_deadline
        else:
            cutoff = self.last_heartbeat_time + self.heartbeat_timeout_interval
        if time.time() > cutoff:
            self.logger.warning(
                "Heartbeat failure; previous heartbeat: %.3fs",
                self.last_heartbeat_time,
            )
            self.exit_code = 1
            self.halt()
            if self.heartbeat_timeout_callback:
                self.heartbeat_timeout_callback()

    def _process_message(self, message: Dict[str, Any]) -> None:
        """Process incoming messages by calling registered handlers."""
        subscription_group = 0
        msg_type = message.get("message_type")
        if msg_type == "TopicIntroduction":
            self.server_topic_id_to_name[message["value"]["topic_id"]] = message[
                "value"
            ]["name"]
            self.server_topic_name_to_id[message["value"]["name"]] = message["value"][
                "topic_id"
            ]
        elif msg_type == "KeyIntroduction":
            subscription_group = self.active_subscription_group
            self.server_key_id_to_name[message["value"]["key_id"]] = message["value"][
                "name"
            ]
            self.server_key_name_to_id[message["value"]["name"]] = message["value"][
                "key_id"
            ]
        elif msg_type == "DeleteKey":
            subscription_group = self.active_subscription_group
            # 1) drop deleted key from server map
            key_id = message["value"]["key_id"]
            self.server_key_name_to_id.pop(
                self.server_key_id_to_name.get(key_id) or "", None
            )
            self.server_key_id_to_name.pop(key_id, None)
        elif msg_type == "Heartbeat":
            # update last‐beat and clear initial grace on the very first one
            self.last_heartbeat_time = time.time()
            if self._initial_grace_period:
                self._initial_grace_period = False
        elif msg_type == "Introduction":
            value = message["value"]
            # 5) Clear out old server state on reconnect
            self.server_topic_id_to_name.clear()
            self.server_topic_name_to_id.clear()
            self.server_key_id_to_name.clear()
            self.server_key_name_to_id.clear()
            self.record_map.clear()
            # reset heartbeat timeout (in seconds)
            self.heartbeat_timeout_interval = max(
                self.heartbeat_timeout_interval,
                value["heartbeat_timeout_interval"] / 1000,
            )
            self.last_heartbeat_time = time.time()
            # 4) enable 10× grace window for the *first* heartbeat
            self._initial_grace_period = True
            self._initial_grace_deadline = (
                self.last_heartbeat_time + self.heartbeat_timeout_interval * 10
            )
        elif msg_type == "JSONRecordUpdate":
            subscription_group = self.active_subscription_group
            record_id = message["value"]["record_id"]
            key_id = record_id["key_id"]
            topic_id = record_id["topic_id"]
            record_value = message["value"]["value"]
            self.record_map[(key_id, topic_id)] = record_value
        elif msg_type == "DeleteRecord":
            subscription_group = self.active_subscription_group
            value = message["value"]
            key_id = value["key_id"]
            topic_id = value["topic_id"]
            self.record_map.pop((key_id, topic_id), None)
        elif msg_type == "BatchUpdate":
            subscription_group = self.active_subscription_group
            value = message["value"]
            default_class = value.get("default_class")

            # Check if there's a specific batch update handler
            batch_handler_key = (
                f"BatchUpdate {subscription_group}"
                if subscription_group
                else "BatchUpdate"
            )
            has_batch_handler = batch_handler_key in self.message_handlers

            # Pre-check for individual handlers if no batch handler
            key_handler = None
            record_handler = None
            if not has_batch_handler:
                key_handler_key = (
                    f"KeyIntroduction {subscription_group}"
                    if subscription_group
                    else "KeyIntroduction"
                )
                key_handler = self.message_handlers.get(key_handler_key)

                record_handler_key = (
                    f"JSONRecordUpdate {subscription_group}"
                    if subscription_group
                    else "JSONRecordUpdate"
                )
                record_handler = self.message_handlers.get(record_handler_key)

            for key_update in value.get("keys", []):
                key_id = key_update["key_id"]
                key_name = key_update.get("name")

                # Handle key introduction if name is provided and key is new
                if key_name and key_id not in self.server_key_id_to_name:
                    self.server_key_id_to_name[key_id] = key_name
                    self.server_key_name_to_id[key_name] = key_id

                    # If no batch handler but key handler exists, call KeyIntroduction handler
                    if not has_batch_handler and key_handler:
                        # Determine class_list: use key's classes, or default_class, or None
                        key_classes = key_update.get("classes")
                        if not key_classes and key_update.get("class"):
                            key_classes = [key_update["class"]]
                        elif not key_classes and default_class:
                            key_classes = [default_class]

                        key_intro_msg = {
                            "message_type": "KeyIntroduction",
                            "value": {
                                "key_id": key_id,
                                "name": key_name,
                                **({"class_list": key_classes} if key_classes else {}),
                            },
                        }
                        key_handler(key_intro_msg)

                # Process topics for this key - topic IDs are now object keys
                topics_dict = key_update.get("topics", {})
                for topic_id_str, record_value in topics_dict.items():
                    topic_id = int(topic_id_str)
                    self.record_map[(key_id, topic_id)] = record_value

                    # If no batch handler but record handler exists, call JSONRecordUpdate handler
                    if not has_batch_handler and record_handler:
                        record_update_msg = {
                            "message_type": "JSONRecordUpdate",
                            "value": {
                                "record_id": {"key_id": key_id, "topic_id": topic_id},
                                "value": record_value,
                            },
                        }
                        record_handler(record_update_msg)

            # If there is a batch handler, call it
            if has_batch_handler:
                batch_handler = self.message_handlers[batch_handler_key]
                batch_handler(message)
        elif msg_type == "ActiveSubscription":
            self.active_subscription_group = message["value"]["subscription_group"]
        elif msg_type == "Logoff":
            self.logger.info("Received Logoff from server")
            self.running = False
        elif msg_type == "Error":
            self.logger.error("GAR %s", message["value"]["message"])
            self.exit_code = 1
            self.stop()

        self.check_heartbeat()

        handler = self.message_handlers.get(
            f"{msg_type} {subscription_group}" if subscription_group else str(msg_type)
        )
        if handler:
            try:
                handler(message)
            except Exception as e:
                self.logger.exception(
                    "Error in handler while processing message %s: %s",
                    str(message),
                    str(e),
                )
                raise

    def subscribe_formatted(self, subscription_message_value: Dict[str, Any]):
        """Send an already-formatted subscription message
        Args:
            subscription_message_value: json representation of the gar `subscribe` struct
        """

        sub_msg = {
            "message_type": "Subscribe",
            "value": subscription_message_value,
        }
        self.logger.debug("Sending: %s", sub_msg)
        self.send_message(sub_msg)

    # pylint: disable=too-many-arguments
    def subscribe(
        self,
        name: str,
        subscription_mode: str = "Streaming",
        key_name: Optional[Union[str, list[str]]] = None,
        topic_name: Optional[Union[str, list[str]]] = None,
        class_name: Optional[Union[str, list[str]]] = None,
        key_filter: Optional[str] = None,
        topic_filter: Optional[str] = None,
        exclude_key_filter: Optional[str] = None,
        exclude_topic_filter: Optional[str] = None,
        max_history: Optional[str] = None,
        include_referenced_keys: bool = False,
        include_referencing_keys: bool = False,
        include_all_namespace: bool = False,
        trim_default_values: bool = False,
        working_namespace: Optional[str] = None,
        density: Optional[str] = None,
        subscription_group: int = 0,
        subscription_set: Optional[str] = None,
        snapshot_size_limit: int = 0,
        nagle_interval: int = 0,
        limit: int = 0,
    ) -> None:
        """Send a subscription request using local IDs.

        Args:
            name: Must be unique among live subscriptions from the client
            subscription_mode: The subscription mode (e.g., "Streaming", "Snapshot")
            mode: Deprecated. Use subscription_mode instead.
            subscription_set: The subscription set identifier
            max_history: Maximum history to include (history_type)
            snapshot_size_limit: If > 0, snapshots will be broken up at this limit
            nagle_interval: Nagle interval in milliseconds
            subscription_group: For receiving notice of which subscription is receiving updates
            density: For performance tuning
            include_referenced_keys: Add keys from any key references in matched records
            include_referencing_keys: Add keys that have one or more records referencing any matched keys
            include_all_namespace: Include keys and topics from all namespaces
            trim_default_values: Trim records containing default values from the snapshot
            limit: Limits the number of records returned in initial snapshot (0 = all)
            key_name: Filter to only these keys if nonempty
            topic_name: Filter to only these topics if nonempty
            class_name: Filter to only topics within these classes if nonempty
            key_filter: Include keys matching this regex (cannot use with key_name)
            exclude_key_filter: Exclude keys matching this regex (cannot use with key_name)
            topic_filter: Include topics matching this regex (cannot use with topic_name)
            exclude_topic_filter: Exclude topics matching this regex (cannot use with topic_name)
            working_namespace: Namespace for matching relative paths using topic filters

        Raises:
            ValueError: If mutually exclusive parameters are used together
        """

        # Validate mutually exclusive parameters
        if key_name and (key_filter or exclude_key_filter):
            raise ValueError(
                "key_name cannot be used with key_filter or exclude_key_filter"
            )

        if topic_name and (topic_filter or exclude_topic_filter):
            raise ValueError(
                "topic_name cannot be used with topic_filter or exclude_topic_filter"
            )

        # Validate limit parameter usage
        if limit > 0 and subscription_mode == "Streaming":
            raise ValueError("limit cannot be used with streaming subscriptions")

        class_list: list[str] | None
        if isinstance(class_name, str):
            class_list = class_name.split()
        else:
            class_list = class_name

        single_class = (
            class_list[0]
            if isinstance(class_list, list) and len(class_list) == 1
            else None
        )

        if isinstance(key_name, str):
            key_names = key_name.split()
        elif key_name:
            key_names = key_name
        else:
            key_names = []

        key_id_list = [
            self.get_and_possibly_introduce_key_id(x, single_class) for x in key_names
        ]

        if isinstance(topic_name, str):
            topic_names = topic_name.split()
        elif topic_name:
            topic_names = topic_name
        else:
            topic_names = []

        topic_id_list = [
            self.get_and_possibly_introduce_topic_id(x) for x in topic_names
        ]

        # Build subscription message, filtering out None values
        value_dict: Dict[str, Any] = {
            "subscription_mode": subscription_mode,
            "name": name,
        }

        # Add optional fields only if they have values
        if subscription_set is not None:
            value_dict["subscription_set"] = subscription_set
        if max_history is not None:
            value_dict["max_history"] = max_history
        if snapshot_size_limit > 0:
            assert (
                snapshot_size_limit <= self.ws_buffer_size
            ), "Snapshot size limit cannot exceed ws_buffer_size"
            value_dict["snapshot_size_limit"] = snapshot_size_limit
        if nagle_interval > 0:
            value_dict["nagle_interval"] = nagle_interval
        if subscription_group > 0:
            value_dict["subscription_group"] = subscription_group
        if density is not None:
            value_dict["density"] = density
        if include_referenced_keys:
            value_dict["include_referenced_keys"] = include_referenced_keys
        if include_referencing_keys:
            value_dict["include_referencing_keys"] = include_referencing_keys
        if include_all_namespace:
            value_dict["include_all_namespace"] = include_all_namespace
        if trim_default_values:
            value_dict["trim_default_values"] = trim_default_values
        if limit > 0:
            value_dict["limit"] = limit
        if key_id_list:
            value_dict["key_id_list"] = key_id_list
        if topic_id_list:
            value_dict["topic_id_list"] = topic_id_list
        if class_list:
            value_dict["class_list"] = class_list
        if key_filter:
            value_dict["key_filter"] = key_filter
        if exclude_key_filter:
            value_dict["exclude_key_filter"] = exclude_key_filter
        if topic_filter:
            value_dict["topic_filter"] = topic_filter
        if exclude_topic_filter:
            value_dict["exclude_topic_filter"] = exclude_topic_filter
        if working_namespace:
            value_dict["working_namespace"] = working_namespace

        self.subscribe_formatted(value_dict)

    def send_subscribe_continue(self, name: str) -> None:
        """Send a SubscribeContinue message for a subscription name."""
        msg = {"message_type": "SubscribeContinue", "value": {"name": name}}
        self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def get_and_possibly_introduce_key_id(
        self, name: str, class_name: Optional[Union[str, list[str]]] = None
    ) -> int:
        """Introduce a new key if not already known and return local key ID."""
        with self._key_lock:
            if name not in self.local_key_map:
                key_id = self.local_key_counter
                self.local_key_map[name] = key_id
                self.local_key_counter += 1
                if class_name:
                    if isinstance(class_name, str):
                        class_list = class_name.split()
                    else:
                        class_list = class_name
                    msg = {
                        "message_type": "KeyIntroduction",
                        "value": {
                            "key_id": key_id,
                            "name": name,
                            "class_list": class_list,
                        },
                    }
                else:
                    msg = {
                        "message_type": "KeyIntroduction",
                        "value": {"key_id": key_id, "name": name},
                    }
                # self.logger.debug("Sending: %s", msg)
                self.send_message(msg)
            return self.local_key_map[name]

    def get_and_possibly_introduce_topic_id(self, name: str) -> int:
        """Introduce a new topic if not already known and return local topic ID."""
        with self._topic_lock:
            if name not in self.local_topic_map:
                topic_id = self.local_topic_counter
                self.local_topic_map[name] = topic_id
                self.local_topic_counter += 1
                msg = {
                    "message_type": "TopicIntroduction",
                    "value": {"topic_id": topic_id, "name": name},
                }
                self.logger.debug("Sending: %s", msg)
                self.send_message(msg)
            return self.local_topic_map[name]

    def publish_delete_key(self, key_id: int) -> None:
        """Publish a DeleteKey message using a local key ID."""
        msg = {"message_type": "DeleteKey", "value": {"key_id": key_id}}
        # self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_delete_record(self, key_id: int, topic_id: int) -> None:
        """Publish a DeleteRecord message using local key and topic IDs."""
        msg = {
            "message_type": "DeleteRecord",
            "value": {"key_id": key_id, "topic_id": topic_id},
        }
        # self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_unsubscribe(self, name: str) -> None:
        """Publish an Unsubscribe message for a subscription name."""
        msg = {"message_type": "Unsubscribe", "value": {"name": name}}
        self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_shutdown(self) -> None:
        """Publish a Shutdown message."""
        msg = {"message_type": "Shutdown"}
        self.logger.debug("Sending: %s", msg)
        self.send_message(msg)

    def publish_record_with_ids(self, key_id: int, topic_id: int, value: Any) -> None:
        """
        Publish a record update using explicit key and topic IDs.

        This method creates and sends a JSONRecordUpdate message to the GAR server
        using the provided key and topic IDs. Unlike publish_record(), this method
        does not perform any name-to-ID conversion or introduce new keys/topics.

        Args:
            key_id: The integer ID of the key for this record. This should be a valid
                   key ID that has already been introduced to the server.
            topic_id: The integer ID of the topic for this record. This should be a valid
                     topic ID that has already been introduced to the server.
            value: The value to publish for this record. Can be any JSON-serializable
                  data type (dict, list, string, number, boolean, or null).

        Returns:
            None
        """
        update_msg = {
            "message_type": "JSONRecordUpdate",
            "value": {
                "record_id": {"key_id": key_id, "topic_id": topic_id},
                "value": value,
            },
        }
        # self.logger.debug("Sending: %s", update_msg)
        self.send_message(update_msg)

    def publish_record(
        self,
        key_name: str,
        topic_name: str,
        value: Any,
        class_name: Optional[str] = None,
    ) -> None:
        """Publish a record update using names, converting to local IDs."""
        key_id = self.get_and_possibly_introduce_key_id(key_name, class_name)
        topic_id = self.get_and_possibly_introduce_topic_id(topic_name)
        self.publish_record_with_ids(key_id, topic_id, value)
