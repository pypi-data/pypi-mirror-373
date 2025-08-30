import unittest
from datetime import datetime, timezone
from juham_automation.automation.energycostcalculator import EnergyCostCalculator
import json


class EnergyCostCalculatorTest(unittest.TestCase):

    def test_constructor(self) -> None:
        """Test construction of EnergyCostCalculator."""
        ok = True
        try:
            object = EnergyCostCalculator()
            self.assertIsNotNone(object)
        except Exception:
            ok = False
        self.assertTrue(ok)

    def create_calculator(self) -> EnergyCostCalculator:
        """Create EnergyCostCalculator with some hourly energy prices."""
        spot: list[dict[str, float]] = []
        spot.append(
            {
                "Timestamp": datetime(
                    2024, 6, 30, 14, 0, tzinfo=timezone.utc
                ).timestamp(),
                "PriceWithTax": 0.10,
            }
        )
        spot.append(
            {
                "Timestamp": datetime(
                    2024, 6, 30, 15, 0, tzinfo=timezone.utc
                ).timestamp(),
                "PriceWithTax": 0.20,
            }
        )
        spot.append(
            {
                "Timestamp": datetime(
                    2024, 6, 30, 16, 0, tzinfo=timezone.utc
                ).timestamp(),
                "PriceWithTax": 0.50,
            }
        )
        spot.append(
            {
                "Timestamp": datetime(
                    2024, 6, 30, 17, 0, tzinfo=timezone.utc
                ).timestamp(),
                "PriceWithTax": 1.00,
            }
        )
        spot.append(
            {
                "Timestamp": datetime(
                    2024, 6, 30, 18, 0, tzinfo=timezone.utc
                ).timestamp(),
                "PriceWithTax": 0.10,
            }
        )
        calculator = EnergyCostCalculator("test")
        calculator.spots = spot
        return calculator

    def test_get_classid(self) -> None:
        """Assert the class identifier is valid."""
        _class_id = EnergyCostCalculator.get_class_id()
        self.assertEqual("EnergyCostCalculator", _class_id)

    def test_cost_per_joule(self) -> None:
        """Test method for mapping energy price per kWh to Ws (Watt seconds,
        i.e. Joules)"""
        obj = self.create_calculator()
        ws = obj.map_kwh_prices_to_joules(1000.0 * 3600)
        self.assertAlmostEqual(1.0, ws, delta=1e-7)

    def test_get_prices(self) -> None:
        obj = self.create_calculator()
        start, stop = obj.get_prices(
            datetime(2024, 6, 30, 14, 0, tzinfo=timezone.utc).timestamp(),
            datetime(2024, 6, 30, 14, 59, tzinfo=timezone.utc).timestamp(),
        )
        expected = 0.1
        self.assertAlmostEqual(expected, start, delta=1e-7)
        self.assertAlmostEqual(expected, stop, delta=1e-7)

    def test_cost_calculator(self) -> None:
        obj = self.create_calculator()

        # energy cost with 1 kW for one hour
        cost = obj.calculate_net_energy_cost(
            datetime(2024, 6, 30, 14, 0, tzinfo=timezone.utc).timestamp(),
            datetime(2024, 6, 30, 15, 0, tzinfo=timezone.utc).timestamp(),
            1000.0,
        )
        self.assertAlmostEqual(0.1, cost, delta=1e-5)

        # cost with 1 kW over two different price boundaries
        cost = obj.calculate_net_energy_cost(
            datetime(2024, 6, 30, 14, 30, tzinfo=timezone.utc).timestamp(),
            datetime(2024, 6, 30, 15, 30, tzinfo=timezone.utc).timestamp(),
            1000.0,
        )
        self.assertAlmostEqual(0.15, cost, delta=1e-5)

        # cost with 1 kW over several hours
        cost = obj.calculate_net_energy_cost(
            datetime(2024, 6, 30, 14, 30, tzinfo=timezone.utc).timestamp(),
            datetime(2024, 6, 30, 17, 30, tzinfo=timezone.utc).timestamp(),
            1000.0,
        )
        expected = 0.5 * 0.1 + 0.2 + 0.5 + 0.5 * 1.0
        self.assertAlmostEqual(expected, cost, delta=1e-5)


if __name__ == "__main__":
    unittest.main()
