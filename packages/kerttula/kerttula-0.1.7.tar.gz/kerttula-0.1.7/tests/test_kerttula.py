import unittest
from unittest.mock import patch, MagicMock
from kerttula import Kerttula
from juham_automation import HeatingOptimizer, WaterCirculator
from juham_shelly import ShellyPlus1, ShellyPro3EM, ShellyMotion, ShellyPro3
from juham_watermeter import WaterMeterImgDiff, WaterMeterTs, LeakDetector


class TestKerttula(unittest.TestCase):

    @patch("masterpiece.Application.load_configuration")
    @patch("kerttula.Kerttula.load_plugins")
    def setUp(self, mock_load_plugins, mock_load_config):
        self.app = Kerttula("test_kerttula")

    def test_initialization(self):
        self.assertEqual(self.app.name, "test_kerttula")

    def test_sensors_added(self):
        sensors = [
            ShellyPro3EM,
            ShellyMotion,
            WaterMeterImgDiff,
            WaterMeterTs,
            LeakDetector,
        ]
        for sensor in sensors:
            with self.subTest(sensor=sensor):
                self.assertTrue(
                    any(isinstance(obj, sensor) for obj in self.app.children)
                )

    def test_automation_components_added(self):
        components = [HeatingOptimizer, WaterCirculator]
        for component in components:
            with self.subTest(component=component):
                self.assertTrue(
                    any(isinstance(obj, component) for obj in self.app.children)
                )

    def test_relay_controllers_added(self):
        relays = [ShellyPlus1, ShellyPro3]
        for relay in relays:
            with self.subTest(relay=relay):
                self.assertTrue(
                    any(isinstance(obj, relay) for obj in self.app.children)
                )

    @patch("kerttula.Kerttula.run_forever")
    @patch(
        "masterpiece.application.Application.parse_args"
    )  # Mock argparse to prevent SystemExit
    def test_main_function(self, mock_parse_args, mock_run_forever):
        with patch("masterpiece.Application.register_plugin_group") as mock_register:
            with patch("kerttula.Kerttula.init_app_id") as mock_init:
                from kerttula import main

                main()
                mock_init.assert_called_once()
                mock_register.assert_called_once()
                mock_run_forever.assert_called_once()


if __name__ == "__main__":
    unittest.main()
