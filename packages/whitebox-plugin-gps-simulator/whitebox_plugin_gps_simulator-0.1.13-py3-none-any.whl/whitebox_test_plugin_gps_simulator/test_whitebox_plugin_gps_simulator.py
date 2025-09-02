from django.test import TestCase
from unittest.mock import patch, MagicMock

from plugin.manager import plugin_manager


class TestWhiteboxPluginGpsSimulator(TestCase):
    def setUp(self) -> None:
        self.plugin = next(
            (
                x
                for x in plugin_manager.whitebox_plugins
                if x.__class__.__name__ == "WhiteboxPluginGpsSimulator"
            ),
            None,
        )
        return super().setUp()

    def test_plugin_loaded(self):
        self.assertIsNotNone(self.plugin)

    def test_plugin_name(self):
        self.assertEqual(self.plugin.name, "GPS Simulator")

    def test_plugin_template(self):
        expected_template = (
            "whitebox_plugin_gps_simulator/whitebox_plugin_gps_simulator.html"
        )
        self.assertEqual(self.plugin.plugin_template, expected_template)

    def test_plugin_js(self):
        expected_js = [
            "/static/whitebox_plugin_gps_simulator/whitebox_plugin_gps_simulator.js"
        ]
        self.assertEqual(self.plugin.plugin_js, expected_js)

    async def test_on_flight_start(self):
        with patch.object(self.plugin, "simulate_gps") as mock_simulate_gps:
            await self.plugin.on_flight_start(None, None)
            self.assertTrue(self.plugin.is_active)
            self.assertIsNotNone(self.plugin.simulation_task)
            mock_simulate_gps.assert_called_once()

    async def test_on_flight_end(self):
        mock_simulation_task = MagicMock()
        mock_simulation_task.done.return_value = False

        self.plugin.is_active = True
        self.plugin.simulation_task = mock_simulation_task

        await self.plugin.on_flight_end(None, None)

        self.assertFalse(self.plugin.is_active)
        self.assertIsNone(self.plugin.simulation_task)
        mock_simulation_task.cancel.assert_called_once_with()

    @patch("plugin.utils.WhiteboxStandardAPI.register_event_callback")
    def test_event_callbacks_registered(self, mock_register_event_callback):
        self.plugin.whitebox.register_event_callback(
            "flight.start",
            self.plugin.on_flight_start,
        )
        self.plugin.whitebox.register_event_callback(
            "flight.end",
            self.plugin.on_flight_end,
        )

        mock_register_event_callback.assert_any_call(
            "flight.start",
            self.plugin.on_flight_start,
        )
        mock_register_event_callback.assert_any_call(
            "flight.end",
            self.plugin.on_flight_end,
        )

    def test_read_gps_simulation(self):
        gps_data = self.plugin.read_gps_simulation(self.plugin.file_path)

        self.assertEqual(gps_data[0], (37.774900, -122.419400, 0.000000))
        self.assertEqual(gps_data[1], (37.776273, -122.407171, 10.500000))

    @patch("asyncio.sleep", return_value=None)
    @patch("location.services.LocationService.emit_location_update")
    async def test_simulate_gps(self, mock_emit_location_update, mock_sleep):
        self.plugin.is_active = True
        self.plugin.gps_data = [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]

        await self.plugin.simulate_gps()

        mock_emit_location_update.assert_called()
        self.assertEqual(mock_emit_location_update.call_count, 2)
        mock_emit_location_update.assert_any_call(1.0, 2.0, 3.0)
        mock_emit_location_update.assert_any_call(4.0, 5.0, 6.0)
