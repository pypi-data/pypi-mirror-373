import unittest
from masterpiece import MqttMsg
from juham_automation.ts.powermeter_ts import PowerMeterTs


class TestPowerMeterTs(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = PowerMeterTs()
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
