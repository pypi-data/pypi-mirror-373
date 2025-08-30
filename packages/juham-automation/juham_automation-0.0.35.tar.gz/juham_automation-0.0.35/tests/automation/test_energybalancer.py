import unittest
from typing import List, Any
from juham_automation.automation.energybalancer import EnergyBalancer
from juham_core.timeutils import (
    quantize,
)
from masterpiece.mqtt import MqttMsg


class SimpleMqttMsg(MqttMsg):
    def __init__(self, topic: str, payload: Any):
        self._topic = topic
        self._payload = payload

    @property
    def payload(self) -> Any:
        return self._payload

    @payload.setter
    def payload(self, value: Any) -> None:
        self._payload = value

    @property
    def topic(self) -> str:
        return self._topic

    @topic.setter
    def topic(self, value: str) -> None:
        self._topic = value


class TestEnergyBalancing(unittest.TestCase):

    balancing_interval: int = EnergyBalancer.energy_balancing_interval
    power: int = 3000  # Power of the radiator (in watts )

    def setUp(self) -> None:
        """Create balancer with two consumers"""
        self.optimizer = EnergyBalancer("test_optimizer")
        self.optimizer.on_consumer({"Unit": "main", "Power": 2000, "Weight": 1.0})
        self.optimizer.on_consumer({"Unit": "sun", "Power": 1000, "Weight":1.0})

    def test_initial_state(self) -> None:
        self.assertEqual(
            self.optimizer.net_energy_balance, 0, "Initial energy balance should be 0"
        )
        self.assertEqual(
            self.balancing_interval, self.optimizer.energy_balancing_interval
        )
        self.assertFalse(self.optimizer.net_energy_balancing_mode)

        self.assertEqual(self.optimizer.needed_energy, 0.0)

        #  time within the interval should be zero
        self.assertEqual(-1, self.optimizer.current_interval_ts)

    def test_set_power(self) -> None:
        """Test setting power consumption and check if the energy balance is updated."""
        step: int = 60
        for ts in range(0, self.balancing_interval, step):
            self.optimizer.update_energy_balance(self.power, ts)
            self.assertEqual(ts * self.power, self.optimizer.net_energy_balance)
            self.assertEqual(ts, self.optimizer.current_interval_ts)

        self.optimizer.update_energy_balance(self.power, ts + step)
        self.assertEqual(0, self.optimizer.net_energy_balance)

    def test_consider_net_energy_balance(self) -> None:
        """Test case to simulate passing time and check energy balancing behavior.
        Pass power consumption self.power, which should switch the heating on just
        in the middle of the interval."""

        balancing_interval: int = self.balancing_interval

        step: int = balancing_interval // 10
        for ts in range(0, self.balancing_interval * 10, step):
            interval_ts: float = ts % balancing_interval  # quantized timestamp
            energy: float = self.power * interval_ts  # in watt-seconds
            self.optimizer.update_energy_balance(self.power, ts)

            # make sure the optimizer is in the right state
            self.assertEqual(energy, self.optimizer.net_energy_balance)

            # Call the method to check if balancing mode should be activated
            main_on: bool = self.optimizer.detect_consumer_status("main", ts)
            sun_on: bool = self.optimizer.detect_consumer_status("sun", ts)

            if energy >= self.optimizer.needed_energy:
                self.assertTrue(main_on or sun_on, "One of the consumers must be ON")
                self.assertFalse(sun_on and main_on, "Only one at a time")
            else:
                self.assertFalse(main_on, "Not enough energy, main should be OFF")
                self.assertFalse(sun_on, "Not enough energy, sun should be OFF")

    def test_quantization(self) -> None:
        """Test that timestamps are quantized to the interval boundaries correctly."""
        test_times: List[int] = [3601, 7200, 10800]  # Slightly over boundaries
        for ts in test_times:
            quantized_ts = quantize(self.optimizer.energy_balancing_interval, ts)
            expected_quantized_ts = (
                ts // self.optimizer.energy_balancing_interval
            ) * self.optimizer.energy_balancing_interval
            self.assertEqual(
                quantized_ts,
                expected_quantized_ts,
                f"Timestamp {ts} should be quantized to {expected_quantized_ts}",
            )
