from juham_automation.automation.energybalancer import EnergyBalancer
from masterpiece import Application
from juham_core import Juham

from .ts import ForecastTs
from .ts import PowerTs
from .ts import PowerPlanTs
from .ts import PowerMeterTs
from .ts import EnergyBalancerTs
from .ts import LogTs
from .ts import EnergyCostCalculatorTs
from .ts import ElectricityPriceTs
from .automation import SpotHintaFi
from .automation import EnergyCostCalculator


class JApp(Application):
    """Juham home automation application base class. Registers new plugin
    group 'juham' on which general purpose Juham plugins can be written on.
    """

    def __init__(self, name: str) -> None:
        """Creates home automation application with the given name.
        If --enable_plugins is False create hard coded configuration
        by calling instantiate_classes() method.

        Args:
            name (str): name for the application
        """
        super().__init__(name, Juham(name))

    def instantiate_classes(self) -> None:
        """Instantiate automation classes .

        Returns:
            None
        """
        self.add(ForecastTs())
        self.add(PowerTs())
        self.add(PowerPlanTs())
        self.add(PowerMeterTs())
        self.add(LogTs())
        self.add(SpotHintaFi())
        self.add(EnergyCostCalculator())
        self.add(EnergyCostCalculatorTs())
        self.add(ElectricityPriceTs())
        self.add(EnergyBalancer())
        self.add(EnergyBalancerTs())

    @classmethod
    def register(cls) -> None:
        """Register plugin group `juham`."""
        Application.register_plugin_group("juham")
