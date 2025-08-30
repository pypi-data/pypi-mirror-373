import unittest
from masterpiece import MqttMsg
from juham_automation.ts.forecast_ts import ForecastTs


class TestForecastTs(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = ForecastTs(name="test_forecast_ts")
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
