import asyncio
import json
import time

import websockets

from django.test import TestCase
from unittest.mock import patch, MagicMock, AsyncMock
from plugin.manager import plugin_manager

from tests.test_utils import (
    side_effects_with_callables,
    DeviceClassResetTestMixin,
    EventRegistryResetTestMixin,
)
from whitebox.events import event_emitter


def gen_close_connection_and_cleanup(plugin):
    """Helper function to close the connection when recv is called."""

    def close_connection_and_cleanup():
        plugin.is_active = False
        raise websockets.exceptions.ConnectionClosed(None, None)

    return close_connection_and_cleanup


class TestWhiteboxPluginStratux(
    EventRegistryResetTestMixin,
    DeviceClassResetTestMixin,
    TestCase,
):
    def setUp(self) -> None:
        super().setUp()

        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginStratux"
            ),
            None,
        )

    def _start_plugin_mechanism_with_websocket_connect_event(self):
        event_emitter.emit_sync("websocket.connect", {})

        # Ensure the plugin is active
        while not self.plugin.is_active:
            time.sleep(0.1)

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_initialization(self):
        with (
            patch.object(self.plugin, "gather_traffic") as mock_gather_traffic,
            patch.object(self.plugin, "gather_situation") as mock_gather_situation,
            patch.object(self.plugin, "gather_status") as mock_gather_status,
        ):
            self._start_plugin_mechanism_with_websocket_connect_event()

        mock_gather_traffic.assert_awaited_once()
        mock_gather_situation.assert_awaited_once()
        mock_gather_status.assert_awaited_once()

        self.assertEqual(self.plugin.name, "Stratux")
        self.assertIsNotNone(self.plugin._plugin_thread)
        self.assertIsNotNone(self.plugin._plugin_loop)

    @patch("websockets.connect")
    async def test_gather_situation_with_decorator(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        situation_data = {
            "GPSLatitude": 37.7749,
            "GPSLongitude": -122.4194,
            "GPSAltitudeMSL": 1000,
        }

        mock_ws.recv.side_effect = side_effects_with_callables(
            [
                json.dumps(situation_data),
                gen_close_connection_and_cleanup(self.plugin),
            ]
        )

        self.plugin.is_active = True
        self.plugin.whitebox.api.location.emit_location_update = AsyncMock()

        # Call the decorated method directly
        with (
            patch("logging.Logger.warning") as mock_warning,
            patch("logging.Logger.info"),
        ):
            await self.plugin.gather_situation()

        mock_warning.assert_called_once_with("WebSocket connection closed")

        # Verify the WebSocket connection was attempted
        mock_connect.assert_called_with(
            f"{self.plugin.STRATUX_URL}/situation",
            ping_timeout=None,
            close_timeout=None,
        )

        # Verify the API was called with the correct data
        self.plugin.whitebox.api.location.emit_location_update.assert_called_with(
            37.7749, -122.4194, 1000
        )

    @patch("websockets.connect")
    async def test_gather_traffic_with_decorator(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        traffic_data = {
            "Tail": "N12345",
            "Icao_addr": "A12345",
            "Lat": 37.7749,
            "Lng": -122.4194,
        }

        mock_ws.recv.side_effect = side_effects_with_callables(
            [
                json.dumps(traffic_data),
                gen_close_connection_and_cleanup(self.plugin),
            ]
        )

        self.plugin.is_active = True
        self.plugin.whitebox.api.traffic.emit_traffic_update = AsyncMock()

        # Call the decorated method directly
        with (
            patch("logging.Logger.warning") as mock_warning,
            patch("logging.Logger.info"),
        ):
            await self.plugin.gather_traffic()

        mock_warning.assert_called_once_with("WebSocket connection closed")

        # Verify the WebSocket connection was attempted
        mock_connect.assert_called_with(
            f"{self.plugin.STRATUX_URL}/traffic", ping_timeout=None, close_timeout=None
        )

        self.plugin.whitebox.api.traffic.emit_traffic_update.assert_called_with(
            traffic_data
        )

    @patch("websockets.connect")
    async def test_gather_status_with_decorator(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        status_data = {
            "GPS_connected": True,
            "GPS_solution": "No Fix",
            "GPS_detected_type": 25,
        }

        mock_ws.recv.side_effect = side_effects_with_callables(
            [
                json.dumps(status_data),
                gen_close_connection_and_cleanup(self.plugin),
            ]
        )

        self.plugin.is_active = True
        self.plugin.whitebox.api.status.emit_status_update = AsyncMock()

        # Call the decorated method directly
        with (
            patch("logging.Logger.warning") as mock_warning,
            patch("logging.Logger.info"),
        ):
            await self.plugin.gather_status()

        mock_warning.assert_called_once_with("WebSocket connection closed")

        # Verify the WebSocket connection was attempted
        mock_connect.assert_called_with(
            f"{self.plugin.STRATUX_URL}/status", ping_timeout=None, close_timeout=None
        )

        self.plugin.whitebox.api.status.emit_status_update.assert_called_with(
            status_data
        )

    @patch("websockets.connect")
    async def test_situation_throttling(self, mock_connect):
        mock_ws = AsyncMock()
        mock_connect.return_value.__aenter__.return_value = mock_ws

        situation_data = {
            "GPSLatitude": 37.7749,
            "GPSLongitude": -122.4194,
            "GPSAltitudeMSL": 1000,
        }

        # Send multiple messages quickly
        mock_ws.recv.side_effect = side_effects_with_callables(
            [
                json.dumps(situation_data),  # First message - should emit
                json.dumps(situation_data),  # Second message - should be throttled
                json.dumps(situation_data),  # Third message - should be throttled
                gen_close_connection_and_cleanup(self.plugin),
            ]
        )

        self.plugin.is_active = True
        self.plugin.whitebox.api.location.emit_location_update = AsyncMock()

        with (
            patch("logging.Logger.warning"),
            patch("logging.Logger.info"),
        ):
            await self.plugin.gather_situation()

        # Should only be called once due to throttling
        self.plugin.whitebox.api.location.emit_location_update.assert_called_once_with(
            37.7749, -122.4194, 1000
        )
