import asyncio

from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter

from tests.test_utils import EventCallbackIsolationMixin
from whitebox.routing import websocket_urlpatterns
from plugin.manager import plugin_manager
from whitebox.api import API


class TestWhiteboxPluginGpsSimulatorIntegration(
    EventCallbackIsolationMixin,
    TransactionTestCase,
):
    event_callback_isolation_types = [
        # These two events are triggered here, and if any other plugins included
        # in the test suite contain their own handlers for this, we can get
        # irrelevant errors within the test run (e.g. `websocket.connect` causing
        # Stratux to start its own mechanism for connecting to Stratux)
        "websocket.connect",
    ]

    def setUp(self) -> None:
        super().setUp()

        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginGpsSimulator"
            ),
            None,
        )
        self.application = URLRouter(websocket_urlpatterns)

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    async def test_websocket_flight_start_triggers_simulation(self):
        communicator = WebsocketCommunicator(self.application, "/ws/flight/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive `on_connect` message
        await communicator.receive_json_from()

        await communicator.send_json_to({"type": "flight.start"})

        # Receive the actual `flight.start` message
        response_info = await communicator.receive_json_from()
        response_flight_data = await communicator.receive_json_from()

        self.assertEqual(response_flight_data["type"], "flight.start")
        self.assertIn("flight_session", response_flight_data)

        self.assertEqual(response_info["type"], "message")
        self.assertEqual(
            response_info["message"],
            "Flight started, enjoy your flight!",
        )

        self.assertTrue(self.plugin.is_active)
        self.assertIsNotNone(self.plugin.simulation_task)

        await asyncio.sleep(1)

        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "location.update")
        self.assertIn("location", response)

        location = response["location"]
        self.assertIn("latitude", location)
        self.assertIn("longitude", location)
        self.assertIn("altitude", location)

        await communicator.disconnect()

    async def test_websocket_flight_end_stops_simulation(self):
        communicator = WebsocketCommunicator(self.application, "/ws/flight/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive `on_connect` message
        await communicator.receive_json_from()

        await communicator.send_json_to({"type": "flight.start"})
        await communicator.receive_json_from()
        await asyncio.sleep(1)

        self.assertTrue(self.plugin.is_active)
        self.assertIsNotNone(self.plugin.simulation_task)

        await communicator.send_json_to({"type": "flight.end"})
        await communicator.receive_json_from()
        await asyncio.sleep(1)

        self.assertFalse(self.plugin.is_active)
        self.assertIsNone(self.plugin.simulation_task)

        await communicator.disconnect()

    async def test_location_updates_stored_in_database(self):
        communicator = WebsocketCommunicator(self.application, "/ws/flight/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Process welcome message
        await communicator.receive_json_from()

        await communicator.send_json_to({"type": "flight.start"})
        await communicator.receive_json_from()
        await asyncio.sleep(1)

        await communicator.send_json_to({"type": "flight.end"})
        await communicator.receive_json_from()
        await asyncio.sleep(1)

        await communicator.disconnect()

        api = API()
        latest_location = await api.location.get_latest_location()
        self.assertIsNotNone(latest_location)
