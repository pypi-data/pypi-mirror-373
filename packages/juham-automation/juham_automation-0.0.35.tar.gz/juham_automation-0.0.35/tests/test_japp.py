import unittest
from juham_automation.japp import JApp


class TestJApp(unittest.TestCase):

    def test_constructor(self) -> None:
        obj = JApp(name="test_japp")
        self.assertIsNotNone(obj)

    def test_instantiate_classes(self) -> None:
        obj = JApp(name="test_japp")
        obj.instantiate_classes()
        self.assertTrue(len(obj.plugins) == 0)


if __name__ == "__main__":
    unittest.main()
