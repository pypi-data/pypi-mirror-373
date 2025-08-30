import unittest
from unittest import TestCase, mock
from unittest.mock import MagicMock, patch
import json
from typing import Dict, Any
from juham_core import JuhamCloudThread

from juham_automation.automation.spothintafi import (
    SpotHintaFiThread,
    SpotHintaFi,
)


class TestSpotHintaFiThread(TestCase):

    @patch("juham_automation.automation.spothintafi.Mqtt")
    def test_make_weburl(self, mock_mqtt) -> None:

        thread = SpotHintaFiThread(mock_mqtt)
        thread.init("test/topic", "http://test.url", 60)

        # Test make_weburl method
        self.assertEqual(thread.make_weburl(), "http://test.url")


class TestSpotHintaFi(unittest.TestCase):

    def test_to_dict(self) -> None:
        spot_hinta = SpotHintaFi("spot")
        spot_hinta.url = "http://test.url"
        expected_dict = {
            "_class": "SpotHintaFi",
            "_version": 0,
            "_object": {"name": "spot", "payload": None},
            "_base": {},
            "_spothintafi": {
                "topic": "/spot",
                "url": "http://test.url",
                "interval": 43200,
            },
        }

        actual_dict: Dict[str, Any] = spot_hinta.to_dict()
        self.assertEqual(actual_dict, expected_dict)

    def test_from_dict(self) -> None:
        spot_hinta = SpotHintaFi()
        data = {
            "_class": "SpotHintaFi",
            "_object": {"name": "rspothintafi"},
            "_base": {},
            "_spothintafi": {
                "topic": "spot/topic",
                "url": "http://test.url",
                "interval": 60,
            },
        }

        spot_hinta.from_dict(data)

        self.assertEqual(spot_hinta.spot_topic, "/spot")
        self.assertEqual(spot_hinta.url, "http://test.url")
        self.assertEqual(spot_hinta.update_interval, 43200)


if __name__ == "__main__":
    unittest.main()
