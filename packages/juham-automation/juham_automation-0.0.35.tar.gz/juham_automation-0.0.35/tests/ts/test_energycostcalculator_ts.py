import unittest
from masterpiece import MqttMsg
from juham_automation.ts.energycostcalculator_ts import EnergyCostCalculatorTs


class TestEnergyCostCalculatorTs(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = EnergyCostCalculatorTs(name="test_ecc_ts")
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
