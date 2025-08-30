import unittest
from masterpiece import MqttMsg
from juham_automation.ts.log_ts import LogTs


class TestLogTs(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = LogTs(name="test_log_ts")
        self.assertIsNotNone(obj)


if __name__ == "__main__":
    unittest.main()
