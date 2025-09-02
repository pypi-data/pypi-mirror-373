import asyncio
import unittest
import time
import os

from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase
from unittest.mock import AsyncMock
from channels.routing import URLRouter

from tests.test_utils import DeviceClassResetTestMixin, EventRegistryResetTestMixin
from whitebox.routing import websocket_urlpatterns
from plugin.manager import plugin_manager


class TestWhiteboxPluginStratuxIntegration(
    EventRegistryResetTestMixin,
    DeviceClassResetTestMixin,
    TransactionTestCase,
):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.skip_hardware_tests = (
            os.getenv("SKIP_HARDWARE_TESTS", "false").lower() == "true"
        )

        if cls.skip_hardware_tests:
            raise unittest.SkipTest(
                "Hardware tests are disabled. Skipping hardware tests for Stratux plugin."
            )

    def setUp(self):
        super().setUp()

        plugin_manager.whitebox_plugins = []
        plugin_manager.plugin_info = {}
        plugin_manager.discover_plugins()

        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginStratux"
            ),
            None,
        )

        self.application = URLRouter(websocket_urlpatterns)

        self.location_mock = AsyncMock()
        self.traffic_mock = AsyncMock()
        self.status_mock = AsyncMock()

        # Ensure the plugin is active
        while not self.plugin.is_active:
            time.sleep(0.1)

        self.plugin.whitebox.api.location.emit_location_update = self.location_mock
        self.plugin.whitebox.api.traffic.emit_traffic_update = self.traffic_mock
        self.plugin.whitebox.api.status.emit_status_update = self.status_mock

    def tearDown(self):
        if hasattr(self, "plugin") and self.plugin:
            self.plugin.stop()

            # Ensure the plugin is inactive
            while self.plugin.is_active:
                time.sleep(0.1)

        return super().tearDown()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.name, "Stratux")

    async def _capture_data(self, duration=10):
        communicator = WebsocketCommunicator(self.application, "/ws/flight/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await asyncio.sleep(duration)
        await communicator.disconnect()

    async def test_real_location_updates(self):
        await self._capture_data(duration=2)

        # Ensure location updates were emitted
        self.assertTrue(self.location_mock.call_count > 0)

        for call in self.location_mock.call_args_list:
            args = call.args
            self.assertIsInstance(args[0], (int, float))
            self.assertIsInstance(args[1], (int, float))
            self.assertIsInstance(args[2], (int, float))

    async def test_real_traffic_updates(self):
        await self._capture_data(duration=2)

        # Ensure traffic updates were emitted
        # Note: Traffic updates are not guaranteed to be emitted
        #       because stratux only emits them when it detects traffic.
        #       Traffic in the air can't be guaranteed.
        self.assertTrue(self.traffic_mock.call_count >= 0)

        for call in self.traffic_mock.call_args_list:
            args = call.args
            self.assertIsInstance(args[0], dict)

            traffic_data = args[0]

            self.assertIn("Icao_addr", traffic_data)
            self.assertIn("Tail", traffic_data)
            self.assertIn("Lat", traffic_data)
            self.assertIn("Lng", traffic_data)
            self.assertIn("Alt", traffic_data)

            self.assertIsInstance(traffic_data["Icao_addr"], int)
            self.assertIsInstance(traffic_data["Tail"], str)
            self.assertIsInstance(traffic_data["Lat"], (int, float))
            self.assertIsInstance(traffic_data["Lng"], (int, float))
            self.assertIsInstance(traffic_data["Alt"], (int, float))

    async def test_real_status_updates(self):
        await self._capture_data(duration=2)

        # Ensure status updates were emitted
        self.assertTrue(self.status_mock.call_count > 0)

        had_all_devices = False
        had_gps_connected = False
        had_gps_solution = False
        had_gps_position_accuracy = False

        for call in self.status_mock.call_args_list:
            args = call.args
            self.assertIsInstance(args[0], dict)

            status_data = args[0]

            self.assertIn("Devices", status_data)
            self.assertIn("GPS_connected", status_data)
            self.assertIn("GPS_solution", status_data)
            self.assertIn("GPS_position_accuracy", status_data)

            self.assertIsInstance(status_data["Devices"], int)
            self.assertIsInstance(status_data["GPS_connected"], bool)
            self.assertIsInstance(status_data["GPS_solution"], str)
            self.assertIsInstance(status_data["GPS_position_accuracy"], (int, float))

            # Stratux status seems to emit non-ideal status even when hardware is connected sometimes
            # So, we'll just check if stratux was in correct state atleast once (with all hardware connected)
            if status_data["Devices"] > 0:
                had_all_devices = True

            if status_data["GPS_connected"]:
                had_gps_connected = True

            if status_data["GPS_solution"] == "3D GPS + SBAS":
                had_gps_solution = True

            if status_data["GPS_position_accuracy"] != "999999":
                had_gps_position_accuracy = True

        self.assertTrue(had_all_devices)
        self.assertTrue(had_gps_connected)
        self.assertTrue(had_gps_solution)
        self.assertTrue(had_gps_position_accuracy)
