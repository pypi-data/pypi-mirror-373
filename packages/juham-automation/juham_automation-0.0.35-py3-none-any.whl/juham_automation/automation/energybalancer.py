import json
from typing import Any
from typing_extensions import override

from juham_core import Juham, timestamp
from masterpiece import MqttMsg


class Consumer:
    """Class representing a consumer.

    This class is used to represent a consumer in the energy balancer.
    It contains the name of the consumer and its power consumption.

    """

    def __init__(self, name: str, power: float, weight: float) -> None:
        """Initialize the consumer

        Args:
            name (str): name of the consumer
            power (float): power of the consumer in watts
        """
        self.name = name
        self.power: float = power
        self.start: float = 0.0
        self.stop: float = 0.0
        self.weight: float = weight


class EnergyBalancer(Juham):
    """The energy balancer monitors the balance between produced and consumed energy
    within the balancing interval to determine if there is enough energy available for
    a given energy-consuming device, such as heating radiators, to operate within the
    remaining time of the interval.

    Any number of energy-consuming devices can be connected to the energy balancer, with
    without any restrictions on the power consumption. The energy balancer will monitor the
    power consumption of the devices and determine if there is enough energy available for
    the devices to operate within the remaining time of the balancing interval.

    The energy balancer is used in conjunction with a power meter that reads
    the total power consumption of the house. The energy balancer uses the power meter


    """

    #: Description of the attribute
    energy_balancing_interval: int = 3600
    """The time interval in seconds for energy balancing."""

    def __init__(self, name: str = "energybalancer") -> None:
        """Initialize the energy balancer.

        Args:
            name (str): name of the heating radiator
            power (float): power of the consumer in watts
        """
        super().__init__(name)

        self.topic_in_consumers = self.make_topic_name("energybalance/consumers")
        self.topic_out_status = self.make_topic_name("energybalance/status")
        self.topic_out_diagnostics = self.make_topic_name("energybalance/diagnostics")
        self.topic_in_power = self.make_topic_name("net_energy_balance")

        self.net_energy_balance: float = 0.0  # Energy balance in joules (watt-seconds)
        self.current_interval_ts: float = -1
        self.needed_energy: float = 0.0  # Energy needed in joules (watt-seconds)
        self.net_energy_balancing_mode: bool = False
        self.consumers: dict[str, Consumer] = {}

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_in_power)
            self.subscribe(self.topic_in_consumers)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        ts: float = timestamp()

        if msg.topic == self.topic_in_power:
            self.on_power(json.loads(msg.payload.decode()), ts)
        elif msg.topic == self.topic_in_consumers:
            self.on_consumer(json.loads(msg.payload.decode()))
        else:
            super().on_message(client, userdata, msg)

    def on_power(self, m: dict[str, Any], ts: float) -> None:
        """Handle the power consumption. Read the current power balance and accumulate
        to the net energy balance to reflect the  energy produced (or consumed) within the
        current time slot.
        Args:
            m (dict[str, Any]): power consumption message
            ts (float): current time
        """
        self.update_energy_balance(m["power"], ts)

    def on_consumer(self, m: dict[str, Any]) -> None:
        """Add consumer, e.g. heating radiator to be controlled.
        Args:
            m (dict[str, Any]): power consumer message
            ts (float): current time
        """
        self.consumers[m["Unit"]] = Consumer(m["Unit"], m["Power"], m["Weight"])
        self.info(
            f"Consumer {m['Unit']} added, power: {m['Power']}, weight: {m['Weight']}"
        )

    def update_energy_balance(self, power: float, ts: float) -> None:
        """Update the current net net energy balance. The change in the balance is calculate the
        energy balance, which the time elapsed since the last update, multiplied by the
        power. Positive energy balance means we have produced energy that can be consumed
        at the end of the interval. The target is to use all the energy produced during the
        balancing interval. This method is called  by the powermeter reading the
        total power consumption of the house.

        Args:
            power (float): power reading from the powermeter. Positive value means
                energy produced, negative value means energy consumed. The value of 0 means
                the house is not consuming or producing energy.
            ts (float): current time in utc seconds
        """

        # regardless of the mode, if we hit the end of the interval, reset the balance

        interval_ts: float = ts % self.energy_balancing_interval
        if self.current_interval_ts < 0 or interval_ts <= self.current_interval_ts:
            # time runs backwards, must be a new interval
            self.reset_net_energy_balance(interval_ts)
        else:
            # update the energy balance with the elapsed time and the power
            elapsed_ts = interval_ts - self.current_interval_ts
            balance: float = elapsed_ts * power  # joules i.e. watt-seconds
            self.net_energy_balance = self.net_energy_balance + balance
            self.current_interval_ts = interval_ts
            self.needed_energy = self.calculate_needed_energy(interval_ts)
            if self.net_energy_balancing_mode:
                if self.net_energy_balance <= 0:
                    # if we have used all the energy, disable the balancing mode
                    self.reset_net_energy_balance(0.0)
            else:
                # consider enabling the balancing mode
                # if we have enough energy to power the radiator for the rest of the time slot
                if self.net_energy_balance >= self.needed_energy:
                    self.net_energy_balancing_mode = True
                    self.initialize_consumer_timelines(ts)
        self.publish_energybalance(ts)

    def calculate_needed_energy(self, interval_ts: float) -> float:
        """Calculate the energy needed to power the consumer for the rest of the time slot.
        Assumes consumers run one at a time in serialized manner and are evenly distributed over the time slot
        to minimze the power peak.

        Args:
            interval_ts (float): current elapsed seconds within the balancing interval.

        Returns:
            float: energy needed in joules
        """

        required_power: float = 0.0
        num_consumers: int = len(self.consumers)
        if num_consumers == 0:
            return 0.0
        remaining_ts_consumer: float = (
            self.energy_balancing_interval - interval_ts
        ) / num_consumers
        total_weight: float = 0.0
        for consumer in self.consumers.values():
            total_weight += consumer.weight
        equal_weight: float = total_weight / num_consumers
        for consumer in self.consumers.values():
            required_power += (
                (consumer.weight / equal_weight)
                * consumer.power
                * remaining_ts_consumer
            )
        return required_power

    def initialize_consumer_timelines(self, ts: float) -> None:
        """Initialize the list of active consumers with their start and stop times.

        Args:
            ts (float): current time.

        Returns:
            None
        """
        num_consumers: int = len(self.consumers)
        if num_consumers == 0:
            return  # If there are no consumers, we simply do nothing
        interval_ts: float = ts % self.energy_balancing_interval
        secs_per_consumer: float = (
            self.energy_balancing_interval - interval_ts
        ) / num_consumers

        total_weight: float = 0.0
        for consumer in self.consumers.values():
            total_weight += consumer.weight
        equal_weight: float = total_weight / num_consumers

        for consumer in self.consumers.values():
            consumer.start = interval_ts
            consumer.stop = (
                interval_ts + secs_per_consumer * consumer.weight / equal_weight
            )
            interval_ts += secs_per_consumer

    def publish_energybalance(self, ts: float) -> None:
        """Publish  diagnostics and status.

        Args:
            ts (float): current time.

        Returns:
            None
        """

        # publish diagnostics
        m: dict[str, Any] = {
            "EnergyBalancer": self.name,
            "CurrentBalance": self.net_energy_balance,
            "NeededBalance": self.needed_energy,
            "Timestamp": ts,
        }
        self.publish(self.topic_out_diagnostics, json.dumps(m))

        # publish consumer statuses to control consumers
        num_consumers: int = len(self.consumers)
        if num_consumers == 0:
            return  # If there are no consumers, we simply do nothing
        interval_ts = ts % self.energy_balancing_interval
        for consumer in self.consumers.values():
            m = {
                "EnergyBalancer": self.name,
                "Unit": consumer.name,
                "Power": consumer.power,
                "Mode": consumer.start <= interval_ts < consumer.stop,
                "Weight": consumer.weight,
                "Timestamp": ts,
            }
            self.publish(self.topic_out_status, json.dumps(m))

    def detect_consumer_status(self, name: str, ts: float) -> bool:
        """Detect consumer status

        Args:
            name (str): name of the consumer
            ts (float): current time.

        Returns:
            True if the consumer is active, False otherwise
        """
        consumer: Consumer = self.consumers[name]
        interval_ts = ts % self.energy_balancing_interval
        return consumer.start <= interval_ts < consumer.stop

    def reset_net_energy_balance(self, interval_ts: float) -> None:
        """Reset the net energy balance at the end of the interval."""
        self.net_energy_balance = 0.0
        self.current_interval_ts = interval_ts
        self.needed_energy = self.calculate_needed_energy(interval_ts)
        self.net_energy_balancing_mode = False
        for consumer in self.consumers.values():
            consumer.start = 0.0
            consumer.stop = 0.0

        self.info("Energy balance reset, interval ended")

    def activate_balancing_mode(self, ts: float) -> None:
        """Activate balancing mode when enough energy is available."""
        self.net_energy_balancing_mode = True
        self.info(
            f"{int(self.net_energy_balance/3600)} Wh is enough to supply the radiator, enable"
        )

    def deactivate_balancing_mode(self) -> None:
        """Deactivate balancing mode when energy is depleted or interval ends."""
        self.net_energy_balancing_mode = False
        self.info("Balance used, or the end of the interval reached, disable")
        self.net_energy_balance = 0.0  # Reset the energy balance at the interval's end
