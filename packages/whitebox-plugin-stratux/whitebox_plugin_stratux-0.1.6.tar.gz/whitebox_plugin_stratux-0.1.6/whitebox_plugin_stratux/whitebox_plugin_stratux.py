import whitebox
import threading
import asyncio
import websockets
import json
import functools
import logging
import os


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Time to wait before reconnecting to the websocket
RECONNECT_SLEEP_TIME: int = 1


def should_emit_now(emit_every: int | None, last_emit_on: float) -> tuple[bool, float]:
    """
    Check if we should emit now based on throttling rules.

    Returns:
        tuple containing (should_emit, new_last_emit_on)
    """
    if emit_every is None:
        return True, last_emit_on

    current_time = asyncio.get_event_loop().time()
    if current_time - last_emit_on < emit_every:
        return False, last_emit_on

    return True, current_time


async def handle_websocket_message(
    websocket, func, self, emit_every, last_emit_on, *args, **kwargs
) -> float:
    """
    Handle a single WebSocket message with throttling.

    Returns:
        Updated last_emit_on timestamp
    """
    try:
        message = await websocket.recv()
        data = json.loads(message)

        should_emit, new_last_emit_on = should_emit_now(emit_every, last_emit_on)
        if not should_emit:
            return last_emit_on

        try:
            await func(self, data, *args, **kwargs)
            return new_last_emit_on
        except Exception:
            logger.exception(f"Error in {func.__name__}")
            return new_last_emit_on

    except websockets.exceptions.ConnectionClosed:
        logger.warning("WebSocket connection closed")
        raise
    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON message")
    except Exception:
        logger.exception("Error processing WebSocket message")

    return last_emit_on


async def websocket_connection_loop(ws_url, self, func, emit_every, *args, **kwargs):
    """
    Handle the WebSocket connection and message processing loop.
    """
    last_emit_on = 0.0

    try:
        async with websockets.connect(
            ws_url, ping_timeout=None, close_timeout=None
        ) as websocket:
            logger.info(f"Connected to {ws_url}")

            while self.is_active:
                try:
                    last_emit_on = await handle_websocket_message(
                        websocket, func, self, emit_every, last_emit_on, *args, **kwargs
                    )
                except websockets.exceptions.ConnectionClosed:
                    break

    except Exception:
        logger.exception(f"Connection error for {ws_url}")
        raise


def websocket_handler(endpoint: str, emit_every: int | None = None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            ws_url = f"{self.STRATUX_URL}/{endpoint}"

            while self.is_active:
                try:
                    await websocket_connection_loop(
                        ws_url, self, func, emit_every, *args, **kwargs
                    )
                except Exception:
                    logger.exception(f"Exception in websocket handler for {endpoint}")
                    await asyncio.sleep(RECONNECT_SLEEP_TIME)

        return wrapper

    return decorator


class WhiteboxPluginStratux(whitebox.Plugin):
    name = "Stratux"

    def __init__(self):
        self.STRATUX_URL = os.getenv("STRATUX_URL", "ws://stratux:80")

        self.is_active = False
        self._plugin_loop = None
        self._plugin_thread = None
        self._plugin_lock = threading.Lock()

    def _start_plugin_loop(self):
        """
        Create a new thread and run the plugin event loop in it.
        """

        def run_plugin_loop():
            self._plugin_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._plugin_loop)

            try:
                self._plugin_loop.run_until_complete(self._create_tasks())
            except Exception as e:
                logger.error(f"Plugin event loop error: {e}")
            finally:
                self._plugin_loop.close()

        with self._plugin_lock:
            if self._plugin_thread:
                return

            self._plugin_thread = threading.Thread(target=run_plugin_loop, daemon=True)
            self._plugin_thread.start()

    async def _create_tasks(self):
        """
        Create tasks for gathering data from the Stratux API.
        """

        self.is_active = True
        tasks = []

        try:
            traffic_task = asyncio.create_task(self.gather_traffic())
            situation_task = asyncio.create_task(self.gather_situation())
            status_task = asyncio.create_task(self.gather_status())
            tasks = [traffic_task, situation_task, status_task]
            await asyncio.gather(*tasks)
        except Exception:
            logger.exception("Failed to create tasks for Stratux plugin")
            self.is_active = False
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()

    async def on_websocket_connect(self, data, ctx):
        # Stratux will be active from the moment the first client connects to
        # any websocket endpoint
        self._start_plugin_loop()

    def stop(self):
        """
        Stop the plugin and clean up resources.
        """
        if self._plugin_loop and not self._plugin_loop.is_closed():
            self._plugin_loop.call_soon_threadsafe(self._plugin_loop.stop)

        if self._plugin_thread and self._plugin_thread.is_alive():
            self._plugin_thread.join(timeout=5)

        self.is_active = False

    def on_load(self):
        self.whitebox.register_event_callback(
            "websocket.connect",
            self.on_websocket_connect,
        )

    def on_unload(self):
        self.whitebox.unregister_event_callback(
            "websocket.connect",
            self.on_websocket_connect,
        )

        self.stop()

    @websocket_handler("situation", emit_every=2)
    async def gather_situation(self, situation_data):
        """
        Note: Situation data emit is throttled because it is updated very frequently
        """
        try:
            await self.whitebox.api.location.emit_location_update(
                situation_data.get("GPSLatitude"),
                situation_data.get("GPSLongitude"),
                situation_data.get("GPSAltitudeMSL"),
            )
        except Exception:
            logger.exception("Failed to emit location update")

    @websocket_handler("traffic")
    async def gather_traffic(self, traffic_data):
        try:
            await self.whitebox.api.traffic.emit_traffic_update(traffic_data)
        except Exception:
            logger.exception("Failed to emit traffic update")

    @websocket_handler("status")
    async def gather_status(self, status_data):
        try:
            await self.whitebox.api.status.emit_status_update(status_data)
        except Exception:
            logger.exception("Failed to emit status update")


plugin_class = WhiteboxPluginStratux
