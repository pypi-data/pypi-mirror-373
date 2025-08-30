import unittest
from masterpiece import MqttMsg
from juham_automation.ts.powerplan_ts import PowerPlanTs


class TestPowerPlanTs(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = PowerPlanTs()
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
