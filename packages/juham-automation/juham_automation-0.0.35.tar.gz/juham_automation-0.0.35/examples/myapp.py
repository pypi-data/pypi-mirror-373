from typing_extensions import override

from juham_automation import JApp
from juham_automation import PowerMeterSimulator
from juham_automation import HeatingOptimizer


class MyApp(JApp):
    """Juham home automation example application."""

    def __init__(self, name: str = "myapp"):
        """Creates home automation application with the given name."""
        super().__init__(name)
        self.instantiate_classes()

    @override
    def instantiate_classes(self) -> None:
        super().instantiate_classes()
        # generate simulated energy meter readings
        self.add(PowerMeterSimulator("powerconsumption"))

        # Heating plan for the main boiler, with shelly's temperature sensor
        self.add(HeatingOptimizer("boiler", "temperature/102", 0, 3, 0.15))

        # print the instance hierarchy
        self.print()


def main() -> None:
    id: str = "myapp"
    MyApp.init_app_id(id)
    app: MyApp = MyApp(id)
    app.run_forever()


if __name__ == "__main__":
    main()
