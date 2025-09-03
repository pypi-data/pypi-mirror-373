import asyncio
import json
import sys
from collections.abc import Callable, Coroutine
from copy import deepcopy
from typing import Any

import msgspec
import websockets
import websockets.protocol
from loguru import logger

from .schema import events
from .schema.events import Events
from .schema.instance_character import (
    ConnectionEventResponse,
    Instance,
    InstanceCharacter,
)
from .schema.intent import Intent, SendIntent, SendIntentValue
from .schema.messages import EventsMessage, ServerMessage, VersionMessage
from .schema.units import GameState, Player

__all__ = ["GameClient", "events"]

SERVER_URL = "wss://programming-game.com"

json_decoder = msgspec.json.Decoder()
json_encoder = msgspec.json.Encoder()

OnLoopHandler = Callable[[GameState], Coroutine[Any, Any, Intent | None]]
OnEventHandler = Callable[[dict], Coroutine[Any, Any, None]]


# noinspection PyPep8Naming
class GameClient:
    def __init__(
        self,
        credentials: dict[str, str],
        offline: bool = False,
        log_level: str = "INFO",
    ):
        self._credentials = credentials
        self._log_level = log_level
        self._websocket: websockets.WebSocketClientProtocol | None = None
        self._tick_task: asyncio.Task | None = None
        self._time = 0
        self._instances: dict[str, Instance] = {}
        self._items: Any = {}
        self._constants: Any = {}
        self._is_running = False
        self._reconnect_delay = 1
        self._on_loop_handler: OnLoopHandler | None = None
        self._on_event_handlers: dict[str, OnEventHandler] = {}

    def on_loop(self, func: OnLoopHandler) -> OnLoopHandler:
        self._on_loop_handler = func
        return func

    def on_event(self, event_name: str = "*"):
        def decorator(func: OnEventHandler) -> OnEventHandler:
            self._on_event_handlers[event_name] = func
            return func

        return decorator

    def _initialize_instance(
        self, instance_id: str, character_id: str
    ) -> InstanceCharacter:
        instance = self._instances.get(instance_id)
        if not instance:
            instance = Instance(time=0)
            self._instances[instance_id] = instance
        if character_id not in instance.characters:
            character = InstanceCharacter(character_id=character_id, instance=instance)
            instance.characters[character_id] = character
        return instance.characters[character_id]

    async def _send(self, message: dict[str, Any]):
        if self._websocket:
            msg_str = json.dumps(message)
            # logger.debug(f"Sending message: {msg_str}")
            await self._websocket.send(msg_str)

    async def _send_msg(self, data: msgspec.Struct):
        if self._websocket:
            msg_str = json_encoder.encode(data).decode("utf-8")
            # logger.debug(f"message: {msg_str}")
            await self._websocket.send(msg_str)

    async def _update_state(
        self, character_instance: InstanceCharacter, event_list: list[Any]
    ):
        for event in event_list:
            handler_name = "handle_" + type(event).__name__.lower()

            if hasattr(character_instance, handler_name):
                cb = getattr(character_instance, handler_name)
                result = cb(event)
                if result and result is ConnectionEventResponse:
                    self._items = result.items
                    self._constants = result.constants
            else:
                print(f"missing {handler_name}")

            if handler := self._on_event_handlers.get(type(event).__name__):
                try:
                    await handler(event)
                except Exception:
                    logger.opt(exception=True).error(
                        f"An error occurred in the on_event callback for event: {type(event).__name__}"
                    )
            if handler := self._on_event_handlers.get("*"):
                try:
                    await handler(event)
                except Exception:
                    logger.opt(exception=True).error(
                        "An error occurred in the on_event callback for event: *"
                    )

    async def _tick_loop(self):
        """The main loop that calls on_tick and sends intents."""
        while (
            self._websocket and self._websocket.state == websockets.protocol.State.OPEN
        ):
            try:
                for instance_id, instance in self._instances.items():
                    # TODO: arena krams

                    for char_id, character_state in instance.characters.items():
                        self._time += 1
                        if instance_id == "overworld" or instance_id.startswith(
                            "instance-"
                        ):
                            units = deepcopy(character_state.units)
                            if char_id not in units:
                                logger.debug(
                                    f"Character {char_id} not found in units in loop"
                                )
                                continue
                            char = Player.from_unit(units[char_id])
                            game_state = GameState(player=char, units=units)
                            if self._on_loop_handler:
                                intent = await self._on_loop_handler(game_state)
                                if intent:
                                    if intent == char.intent:
                                        continue
                                    logger.debug(f"Sending intent: {intent}")
                                    await self._send_msg(
                                        SendIntent(
                                            value=SendIntentValue(
                                                c=char_id,
                                                i=instance_id,
                                                unitId=char_id,
                                                intent=intent,
                                            )
                                        )
                                    )

                await asyncio.sleep(0.3)
            except Exception:
                logger.opt(exception=True).error(
                    "An error occurred in the tick loop (probably in your on_tick logic). Pausing for 5 seconds."
                )
                await asyncio.sleep(5)

    async def handle_message(self, message: ServerMessage) -> None:
        if type(message) is EventsMessage:
            for instance_id, chars in message.value.items():
                for char_id, events in chars.items():
                    character_instance = self._initialize_instance(instance_id, char_id)
                    await self._update_state(character_instance, events)
        elif type(message) is VersionMessage:
            logger.info(f"Server version: {message.value}")

    def _configure_logger(self):
        logger.remove()
        logger.add(sys.stderr, level=self._log_level)

    async def connect(self):
        self._configure_logger()
        self._is_running = True
        while self._is_running:
            logger.info(f"Connecting to server at {SERVER_URL}...")
            try:
                async with websockets.connect(SERVER_URL) as websocket:
                    self._websocket = websocket
                    self._reconnect_delay = (
                        1  # Reset reconnect delay on successful connection
                    )
                    logger.success("Connection established successfully!")
                    await self._send(
                        {
                            "type": "credentials",
                            "value": self._credentials,
                            "version": "0.0.1",
                        }
                    )

                    def log_task_exception(task: asyncio.Task):
                        if not task.cancelled() and (exc := task.exception()):
                            logger.opt(exception=exc).error(
                                "The tick loop task has ended unexpectedly!"
                            )

                    self._tick_task = asyncio.create_task(self._tick_loop())
                    self._tick_task.add_done_callback(log_task_exception)

                    async for message_str in websocket:
                        message = json_decoder.decode(message_str)
                        if message.get("type") == "events":
                            for instance_id, chars in message.get("value", {}).items():
                                for char_id, events in chars.items():
                                    replace = []
                                    for event in events:
                                        event[1]["type"] = event[0]
                                        try:
                                            msgspec.convert(event[1], type=Events)
                                            replace.append(event[1])
                                        except msgspec.ValidationError:
                                            logger.warning(
                                                "Error deconding event: {} {}",
                                                event[0],
                                                event[1],
                                            )
                                    chars[char_id] = replace

                        try:
                            message = msgspec.convert(message, type=ServerMessage)
                        except msgspec.ValidationError:
                            logger.opt(exception=True).error(
                                f"Invalid message: {message}"
                            )
                            continue
                        await self.handle_message(message)

            except websockets.exceptions.ConnectionClosed as e:
                logger.warning(
                    f"Connection closed: {e}. Reconnecting in {self._reconnect_delay} seconds..."
                )
            except ConnectionRefusedError:
                logger.error(
                    f"Connection refused. Reconnecting in {self._reconnect_delay} seconds..."
                )
            except Exception:
                logger.opt(exception=True).error(
                    f"A critical error occurred. Reconnecting in {self._reconnect_delay} seconds..."
                )
            finally:
                if self._tick_task and not self._tick_task.done():
                    self._tick_task.cancel()
                self._websocket = None
                if self._is_running:
                    await asyncio.sleep(self._reconnect_delay)
                    self._reconnect_delay = min(
                        self._reconnect_delay * 2, 60
                    )  # Exponential backoff, max 60s

    async def disconnect(self):
        """Gracefully disconnects from the server."""
        logger.info("Disconnecting from server...")
        self._is_running = False
        if self._tick_task and not self._tick_task.done():
            self._tick_task.cancel()
        if self._websocket and self._websocket.state == websockets.protocol.State.OPEN:
            await self._websocket.close()
        self._websocket = None
        logger.info("Disconnected successfully.")
