from typing import Any
from typing_extensions import override
import json
from masterpiece.mqtt import MqttMsg
from juham_core import Juham
from juham_core.timeutils import (
    elapsed_seconds_in_day,
    elapsed_seconds_in_hour,
    quantize,
    timestamp,
)


class EnergyCostCalculator(Juham):
    """The EnergyCostCalculator class calculates the net energy balance and cost between produced
    (or consumed) energy for Time-Based Settlement (TBS). It performs the following functions:

    * Subscribes to 'spot' and 'power' MQTT topics.
    * Calculates the net energy and the rate of change of the net energy per hour and per day (24h)
    * Calculates the cost of energy consumed/produced based on the spot prices.
    * Publishes the calculated values to the MQTT net energy balance and cost topics.


    This information helps other home automation components optimize energy usage and
    minimize electricity bills.
    """

    _kwh_to_joule_coeff: float = 1000.0 * 3600
    _joule_to_kwh_coeff: float = 1.0 / _kwh_to_joule_coeff

    energy_balancing_interval: float = 3600

    def __init__(self, name: str = "ecc") -> None:
        super().__init__(name)
        self.current_ts: float = 0
        self.total_balance_hour: float = 0
        self.total_balance_day: float = 0
        self.net_energy_balance_cost_hour: float = 0
        self.net_energy_balance_cost_day: float = 0
        self.net_energy_balance_start_hour = elapsed_seconds_in_hour(timestamp())
        self.net_energy_balance_start_day = elapsed_seconds_in_day(timestamp())
        self.spots: list[dict[str, float]] = []
        self.init_topics()

    def init_topics(self) -> None:
        self.topic_in_spot = self.make_topic_name("spot")
        self.topic_in_powerconsumption = self.make_topic_name("powerconsumption")
        self.topic_out_net_energy_balance = self.make_topic_name("net_energy_balance")
        self.topic_out_energy_cost = self.make_topic_name("net_energy_cost")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_in_spot)
            self.subscribe(self.topic_in_powerconsumption)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        ts_now = timestamp()

        m = json.loads(msg.payload.decode())
        if msg.topic == self.topic_in_spot:
            self.on_spot(m)
        elif msg.topic == self.topic_in_powerconsumption:
            self.on_powerconsumption(ts_now, m)
        else:
            self.error(f"Unknown event {msg.topic}")

    def on_spot(self, spot: dict[Any, Any]) -> None:
        """Stores the received per hour electricity prices to spots list.

        Args:
            spot (list): list of hourly spot prices
        """

        for s in spot:
            self.spots.append(
                {"Timestamp": s["Timestamp"], "PriceWithTax": s["PriceWithTax"]}
            )

    def map_kwh_prices_to_joules(self, price: float) -> float:
        """Convert the given electricity price in kWh to Watt seconds (J)
        Args:
            price (float): electricity price given as kWh
        Returns:
            Electricity price per watt second (J)
        """
        return price * self._joule_to_kwh_coeff

    def get_prices(self, ts_prev: float, ts_now: float) -> tuple[float, float]:
        """Fetch the electricity prices for the given two subsequent time
        stamps.

        Args:
            ts_prev (float): previous time
            ts_now (float): current time
        Returns:
            Electricity prices for the given interval
        """
        prev_price = None
        current_price = None

        for i in range(0, len(self.spots) - 1):
            r0 = self.spots[i]
            r1 = self.spots[i + 1]
            ts0 = r0["Timestamp"]
            ts1 = r1["Timestamp"]
            if ts_prev >= ts0 and ts_prev <= ts1:
                prev_price = r0["PriceWithTax"]
            if ts_now >= ts0 and ts_now <= ts1:
                current_price = r0["PriceWithTax"]
            if prev_price is not None and current_price is not None:
                return prev_price, current_price
        self.error("PANIC: run out of spot prices")
        return 0.0, 0.0

    def calculate_net_energy_cost(
        self, ts_prev: float, ts_now: float, energy: float
    ) -> float:
        """Given time interval as start and stop Calculate the cost over the
        given time period. Positive values indicate revenue, negative cost.

        Args:
            ts_prev (timestamp): beginning time stamp of the interval
            ts_now (timestamp): end of the interval
            energy (float): energy consumed during the time interval
        Returns:
            Cost or revenue
        """
        cost: float = 0
        prev = ts_prev
        while prev < ts_now:
            elapsed_seconds: float = ts_now - prev
            if elapsed_seconds > self.energy_balancing_interval:
                elapsed_seconds = self.energy_balancing_interval
            now = prev + elapsed_seconds
            start_per_kwh, stop_per_kwh = self.get_prices(prev, now)
            start_price = self.map_kwh_prices_to_joules(start_per_kwh)
            stop_price = self.map_kwh_prices_to_joules(stop_per_kwh)
            if abs(stop_price - start_price) < 1e-24:
                cost = cost + energy * elapsed_seconds * start_price
            else:
                # interpolate cost over energy balancing interval boundary
                elapsed = now - prev
                if elapsed < 0.00001:
                    return 0.0
                ts_0 = quantize(self.energy_balancing_interval, now)
                t1 = (ts_0 - prev) / elapsed
                t2 = (now - ts_0) / elapsed
                cost = (
                    cost
                    + energy
                    * ((1.0 - t1) * start_price + t2 * stop_price)
                    * elapsed_seconds
                )

            prev = prev + elapsed_seconds
        return cost

    def on_powerconsumption(self, ts_now: float, m: dict[Any, Any]) -> None:
        """Calculate net energy cost and update the hourly consumption attribute
        accordingly.

        Args:
           ts_now (float): time stamp of the energy consumed
           m (dict): Juham MQTT message holding energy reading
        """
        power = m["real_total"]
        if not self.spots:
            self.info("Waiting for electricity prices...")
        elif self.current_ts == 0:
            self.net_energy_balance_cost_hour = 0.0
            self.net_energy_balance_cost_day = 0.0
            self.current_ts = ts_now
            self.net_energy_balance_start_hour = quantize(
                self.energy_balancing_interval, ts_now
            )
        else:
            # calculate cost of energy consumed/produced
            dp: float = self.calculate_net_energy_cost(self.current_ts, ts_now, power)
            self.net_energy_balance_cost_hour = self.net_energy_balance_cost_hour + dp
            self.net_energy_balance_cost_day = self.net_energy_balance_cost_day + dp

            # calculate and publish energy balance
            dt = ts_now - self.current_ts  # time elapsed since previous call
            balance = dt * power  # energy consumed/produced in this slot in Joules
            self.total_balance_hour = (
                self.total_balance_hour + balance * self._joule_to_kwh_coeff
            )
            self.total_balance_day = (
                self.total_balance_day + balance * self._joule_to_kwh_coeff
            )
            self.publish_net_energy_balance(ts_now, self.name, balance, power)
            self.publish_energy_cost(
                ts_now,
                self.name,
                self.net_energy_balance_cost_hour,
                self.net_energy_balance_cost_day,
            )

            # Check if the current energy balancing interval has ended
            # If so, reset the net_energy_balance attribute for the next interval
            if (
                ts_now - self.net_energy_balance_start_hour
                > self.energy_balancing_interval
            ):
                # publish average energy cost per hour
                if abs(self.total_balance_hour) > 0:
                    msg = {
                        "name": self.name,
                        "average_hour": self.net_energy_balance_cost_hour
                        / self.total_balance_hour,
                        "ts": ts_now,
                    }
                    self.publish(self.topic_out_energy_cost, json.dumps(msg), 0, False)

                # reset for the next hour
                self.total_balance_hour = 0
                self.net_energy_balance_cost_hour = 0.0
                self.net_energy_balance_start_hour = ts_now

            if ts_now - self.net_energy_balance_start_day > 24 * 3600:
                if abs(self.total_balance_day) > 0:
                    msg = {
                        "name": self.name,
                        "average_day": self.net_energy_balance_cost_day
                        / self.total_balance_day,
                        "ts": ts_now,
                    }
                    self.publish(self.topic_out_energy_cost, json.dumps(msg), 0, False)
                # reset for the next day
                self.total_balance_day = 0
                self.net_energy_balance_cost_day = 0.0
                self.net_energy_balance_start_day = ts_now

            self.current_ts = ts_now

    def publish_net_energy_balance(
        self, ts_now: float, site: str, energy: float, power: float
    ) -> None:
        """Publish the net energy balance for the current energy balancing interval, as well as
        the real-time power at which energy is currently being produced or consumed (the
        rate of change of net energy).

        Args:
            ts_now (float): timestamp
            site (str): site
            energy (float): cost or revenue.
            power (float) : momentary power (rage of change of energy)
        """
        msg = {"site": site, "power": power, "energy": energy, "ts": ts_now}
        self.publish(self.topic_out_net_energy_balance, json.dumps(msg), 1, True)

    def publish_energy_cost(
        self, ts_now: float, site: str, cost_hour: float, cost_day: float
    ) -> None:
        """Publish daily and hourly energy cost/revenue

        Args:
            ts_now (float): timestamp
            site (str): site
            cost_hour (float): cost or revenue per hour.
            cost_day (float) : cost or revenue per day
        """
        msg = {"name": site, "cost_hour": cost_hour, "cost_day": cost_day, "ts": ts_now}
        self.publish(self.topic_out_energy_cost, json.dumps(msg), 1, True)
