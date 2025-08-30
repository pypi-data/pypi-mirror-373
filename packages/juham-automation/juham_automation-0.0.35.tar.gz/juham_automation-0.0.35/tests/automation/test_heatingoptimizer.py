import json
import unittest
from typing import Any
from masterpiece import MqttMsg
from unittest.mock import MagicMock, patch
from masterpiece.mqtt import MqttMsg
from juham_automation.automation.heatingoptimizer import HeatingOptimizer


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


class TestHeatingOptimizer(unittest.TestCase):
    def setUp(self) -> None:
        self.optimizer = HeatingOptimizer(
            name="test_optimizer",
            temperature_sensor="temp_sensor",
            start_hour=5,
            num_hours=3,
            spot_limit=0.25,
        )

        # Use patch.object to mock instance methods dynamically
        self.patcher_subscribe = patch.object(
            self.optimizer, "subscribe", autospec=True
        )
        self.patcher_debug = patch.object(self.optimizer, "debug", autospec=True)
        self.patcher_info = patch.object(self.optimizer, "info", autospec=True)
        self.patcher_error = patch.object(self.optimizer, "error", autospec=True)
        self.patcher_warning = patch.object(self.optimizer, "warning", autospec=True)

        # Start the patches
        self.mock_subscribe = self.patcher_subscribe.start()
        self.mock_debug = self.patcher_debug.start()
        self.mock_info = self.patcher_info.start()
        self.mock_error = self.patcher_error.start()
        self.mock_warning = self.patcher_warning.start()

    def tearDown(self) -> None:
        # Stop the patches to clean up
        self.patcher_subscribe.stop()
        self.patcher_debug.stop()
        self.patcher_info.stop()
        self.patcher_error.stop()
        self.patcher_warning.stop()

    def test_initialization(self) -> None:
        self.assertEqual(self.optimizer.heating_hours_per_day, 3)
        self.assertEqual(self.optimizer.start_hour, 5)
        self.assertEqual(self.optimizer.spot_limit, 0.25)
        self.assertEqual(self.optimizer.current_temperature, 100)
        self.assertFalse(self.optimizer.relay)

    def test_on_connect(self) -> None:
        self.optimizer.on_connect(None, None, 0, 0)
        self.mock_subscribe.assert_any_call(self.optimizer.topic_in_spot)
        self.mock_subscribe.assert_any_call(self.optimizer.topic_in_forecast)
        self.mock_subscribe.assert_any_call(self.optimizer.topic_in_temperature)
        self.mock_subscribe.assert_any_call(self.optimizer.topic_in_energybalance)

    def test_sort_by_rank(self) -> None:
        test_data = [
            {"Rank": 2, "Timestamp": 2000},
            {"Rank": 1, "Timestamp": 3000},
            {"Rank": 3, "Timestamp": 1000},
        ]
        sorted_data = self.optimizer.sort_by_rank(test_data, 1500)
        self.assertEqual(sorted_data[0]["Rank"], 1)
        self.assertEqual(sorted_data[1]["Rank"], 2)

    def test_sort_by_power(self) -> None:
        test_data = [
            {"solarenergy": 50, "ts": 2000},
            {"solarenergy": 100, "ts": 3000},
            {"solarenergy": 10, "ts": 1000},
        ]
        sorted_data = self.optimizer.sort_by_power(test_data, 1500)
        self.assertEqual(sorted_data[0]["solarenergy"], 100)
        self.assertEqual(sorted_data[1]["solarenergy"], 50)

    def test_on_message_temperature_update(self) -> None:
        mock_msg = SimpleMqttMsg(
            topic=self.optimizer.topic_in_temperature, payload=b'{"temperature": 55}'
        )
        self.optimizer.on_message(None, None, mock_msg)
        self.assertEqual(self.optimizer.current_temperature, 55)

    def test_consider_net_energy_balance(self) -> None:
        """Test case to simulate passing time and check energy balancing behavior."""
        data: dict[str, Any] = {"Unit": "main", "Mode": False}
        mock_msg = SimpleMqttMsg(
            topic=self.optimizer.topic_in_energybalance,
            payload=json.dumps(data).encode("utf-8"),
        )
        self.optimizer.on_message(None, None, mock_msg)
        self.assertFalse(
            self.optimizer.net_energy_balance_mode,
            f"At time {0}, heating should be OFF",
        )
        self.optimizer.on_message(
            None,
            None,
            SimpleMqttMsg(
                topic=self.optimizer.topic_in_energybalance,
                payload=json.dumps({"Unit": "sun", "Mode": True}).encode("utf-8"),
            ),
        )
        self.assertFalse(
            self.optimizer.net_energy_balance_mode,
            f"At time {0}, heating should be OFF",
        )


if __name__ == "__main__":
    unittest.main()
