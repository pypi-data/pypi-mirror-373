import unittest
from masterpiece import MqttMsg
from juham_automation.ts.power_ts import PowerTs


class TestPowerTs(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = PowerTs(name="test_power_ts")
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
