from datetime import datetime
import json
from typing import Any
from typing_extensions import override

from masterpiece.mqtt import MqttMsg
from juham_core import Juham
from juham_core.timeutils import (
    quantize,
    timestamp,
    timestamp_hour,
    timestampstr,
    is_hour_within_schedule,
    timestamp_hour_local,
)


class HeatingOptimizer(Juham):
    """Automation class for optimized control of temperature driven home energy consumers e.g hot
    water radiators. Reads spot prices, solar electricity forecast,  power meter and
    temperature to minimize electricity bill.

    Represents a heating system that knows the power rating of its radiator (e.g., 3kW).
    Any number of heating devices can be controlled, each with its own temperature, schedule and electricity price ratings

    The system subscribes to the 'power' topic to track the current power balance. If the solar panels
    generate more energy than is being consumed, the optimizer activates a relay to ensure that all excess energy
    produced within that balancing interval is used for heating. The goal is to achieve a net zero energy balance for each hour,
    ensuring that any surplus energy from the solar panels is fully utilized.

    Computes also UOI - optimization utilization index for each hour, based on the spot price and the solar power forecast.
    For negative energy balance this determines when energy is consumed. Value of 0 means the hour is expensive, value of 1 means
    the hour is free. The UOI threshold determines the slots that are allowed to be consumed.
    """

    energy_balancing_interval: float = 3600
    """Energy balancing interval, as regulated by the  industry/converment. In seconds"""

    radiator_power: float = 6000  # W
    """Radiator power in Watts. This is the maximum power that the radiator can consume."""

    heating_hours_per_day: float = 4
    """ Number of hours per day the radiator is allowed to heat."""

    schedule_start_hour: float = 0
    """Start hour of the heating schedule."""

    schedule_stop_hour: float = 0
    """Stop hour of the heating schedule. Heating is allowed only between these two hours."""

    timezone: str = "Europe/Helsinki"
    """ Timezone of the heating system. This is used to convert UTC timestamps to local time."""

    expected_average_price: float = 0.2
    """Expected average price of electricity, beyond which the heating is avoided."""

    uoi_threshold: float = 0.8
    """Utilization Optimization Index threshold. This is the minimum UOI value that is allowed for the heating to be activated."""

    balancing_weight: float = 1.0
    """Weight determining how large a share of the time slot a consumer receives compared to others ."""

    temperature_limits: dict[int, tuple[float, float]] = {
        1: (68.0, 70.0),  # January
        2: (68.0, 70.0),  # February
        3: (65.0, 70.0),  # March
        4: (60.0, 70.0),  # April
        5: (50.0, 70.0),  # May
        6: (40.0, 60.0),  # June
        7: (40.0, 60.0),  # July
        8: (60.0, 65.0),  # August
        9: (60.0, 65.0),  # September
        10: (65.0, 66.0),  # October
        11: (66.0, 68.0),  # November
        12: (67.0, 70.0),  # December
    }
    """Temperature limits for each month. The minimum temperature is maintained regardless of the cost.
    The limits are defined as a dictionary where the keys are month numbers (1-12)
    and the values are tuples of (min_temp, max_temp). The min_temp and max_temp values are in degrees Celsius."""

    def __init__(
        self,
        name: str,
        temperature_sensor: str,
        start_hour: int,
        num_hours: int,
        spot_limit: float,
    ) -> None:
        """Create power plan for automating temperature driven systems, e.g. heating radiators
        to optimize energy consumption based on electricity prices.

        Electricity Price MQTT Topic: This specifies the MQTT topic through which the controller receives
        hourly electricity price forecasts for the next day or two.
        Radiator Control Topic: The MQTT topic used to control the radiator relay.
        Temperature Sensor Topic: The MQTT topic where the temperature sensor publishes its readings.
        Electricity Price Slot Range: A pair of integers determining which electricity price slots the
        controller uses. The slots are ranked from the cheapest to the most expensive. For example:
        - A range of 0, 3 directs the controller to use electricity during the three cheapest hours.
        - A second controller with a range of 3, 2 would target the next two cheapest hours, and so on.
        Maximum Electricity Price Threshold: An upper limit for the electricity price, serving as an additional control.
        The controller only operates within its designated price slots if the prices are below this threshold.

        The maximum price threshold reflects the criticality of the radiator's operation:

        High thresholds indicate that the radiator should remain operational regardless of the price.
        Low thresholds imply the radiator can be turned off during expensive periods, suggesting it has a less critical role.

        By combining these attributes, the controller ensures efficient energy usage while maintaining desired heating levels.

        Args:
            name (str): name of the heating radiator
            temperature_sensor (str): temperature sensor of the heating radiator
            start_hour (int): ordinal of the first allowed electricity price slot to be consumed
            num_hours (int): the number of slots allowed
            spot_limit (float): maximum price allowed
        """
        super().__init__(name)

        self.heating_hours_per_day = num_hours
        self.start_hour = start_hour
        self.spot_limit = spot_limit

        self.topic_in_spot = self.make_topic_name("spot")
        self.topic_in_forecast = self.make_topic_name("forecast")
        self.topic_in_temperature = self.make_topic_name(temperature_sensor)
        self.topic_powerplan = self.make_topic_name("powerplan")
        self.topic_in_energybalance = self.make_topic_name("energybalance/status")
        self.topic_out_energybalance = self.make_topic_name("energybalance/consumers")
        self.topic_out_power = self.make_topic_name("power")

        self.current_temperature = 100
        self.current_heating_plan = 0
        self.current_relay_state = -1
        self.heating_plan: list[dict[str, int]] = []
        self.power_plan: list[dict[str, Any]] = []
        self.ranked_spot_prices: list[dict[Any, Any]] = []
        self.ranked_solarpower: list[dict[Any, Any]] = []
        self.relay: bool = False
        self.relay_started_ts: float = 0
        self.net_energy_balance_mode: bool = False

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_in_spot)
            self.subscribe(self.topic_in_forecast)
            self.subscribe(self.topic_in_temperature)
            self.subscribe(self.topic_in_energybalance)
            self.register_as_consumer()

    def register_as_consumer(self) -> None:
        """Register this device as a consumer to the energy balancer. The energy balancer will then add this device
        to its list of consumers and will tell the device when to heat."""

        consumer: dict[str, Any] = {
            "Unit": self.name,
            "Power": self.radiator_power,
            "Weight": self.balancing_weight,
        }
        self.publish(self.topic_out_energybalance, json.dumps(consumer), 1, False)
        self.info(
            f"Registered {self.name} as consumer with {self.radiator_power}W power",
            "",
        )

    # Function to get the temperature limits based on the current month
    def get_temperature_limits_for_current_month(self) -> tuple[float, float]:
        """Get the temperature limits for the current month.
        The limits are defined in a dictionary where the keys are month numbers (1-12)
        and the values are tuples of (min_temp, max_temp).
        Returns: tuple: (min_temp, max_temp)
        """
        current_month: int = datetime.now().month
        # Get the min and max temperatures for the current month
        min_temp, max_temp = self.temperature_limits[current_month]
        return min_temp, max_temp

    def sort_by_rank(
        self, hours: list[dict[str, Any]], ts_utc_now: float
    ) -> list[dict[str, Any]]:
        """Sort the given electricity prices by their rank value. Given a list
        of electricity prices, return a sorted list from the cheapest to the
        most expensive hours. Entries that represent electricity prices in the
        past are excluded.

        Args:
            hours (list): list of hourly electricity prices
            ts_utc_now (float): current time

        Returns:
            list: sorted list of electricity prices
        """
        sh = sorted(hours, key=lambda x: x["Rank"])
        ranked_hours: list[dict[str, Any]] = []
        for h in sh:
            utc_ts = h["Timestamp"]
            if utc_ts > ts_utc_now:
                ranked_hours.append(h)

        return ranked_hours

    def sort_by_power(
        self, solarpower: list[dict[Any, Any]], ts_utc: float
    ) -> list[dict[Any, Any]]:
        """Sort forecast of solarpower to decreasing order.

        Args:
            solarpower (list): list of entries describing hourly solar energy forecast
            ts_utc(float): start time, for exluding entries that are in the past

        Returns:
            list: list from the highest solarenergy to lowest.
        """

        # if all items have solarenergy key then
        # sh = sorted(solarpower, key=lambda x: x["solarenergy"], reverse=True)
        # else skip items that don't have solarenergy key
        sh = sorted(
            [item for item in solarpower if "solarenergy" in item],
            key=lambda x: x["solarenergy"],
            reverse=True,
        )
        self.debug(
            f"{self.name} sorted {len(sh)} days of forecast starting at {timestampstr(ts_utc)}"
        )
        ranked_hours: list[dict[str, Any]] = []

        for h in sh:
            utc_ts: float = float(h["ts"])
            if utc_ts >= ts_utc:
                ranked_hours.append(h)
        self.debug(
            f"{self.name} forecast sorted for the next {str(len(ranked_hours))} hours"
        )
        return ranked_hours

    def on_spot(self, m: list[dict[str, Any]], ts_quantized: float) -> None:
        """Handle the spot prices.

        Args:
            list[dict[str, Any]]: list of spot prices
            ts_quantized (float): current time
        """
        self.ranked_spot_prices = self.sort_by_rank(m, ts_quantized)

    def on_forecast(
        self, forecast: list[dict[str, Any]], ts_utc_quantized: float
    ) -> None:
        """Handle the solar forecast.

        Args:
            m (list[dict[str, Any]]): list of forecast prices
            ts_quantized (float): current time
        """
        # reject forecasts that don't have solarenergy key
        for f in forecast:
            if not "solarenergy" in f:
                return

        self.ranked_solarpower = self.sort_by_power(forecast, ts_utc_quantized)
        self.debug(
            f"{self.name} solar energy forecast received and ranked for {len(self.ranked_solarpower)} hours"
        )
        self.power_plan = []  # reset power plan, it depends on forecast

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        m = None
        ts: float = timestamp()
        ts_utc_quantized: float = quantize(3600, ts - 3600)
        if msg.topic == self.topic_in_spot:
            self.on_spot(json.loads(msg.payload.decode()), ts_utc_quantized)
            return
        elif msg.topic == self.topic_in_forecast:
            self.on_forecast(json.loads(msg.payload.decode()), ts_utc_quantized)
            return
        elif msg.topic == self.topic_in_temperature:
            m = json.loads(msg.payload.decode())
            self.current_temperature = m["temperature"]
        elif msg.topic == self.topic_in_energybalance:
            decoded_payload = msg.payload.decode()
            m = json.loads(decoded_payload)
            self.on_netenergy_balance(m)
        else:
            super().on_message(client, userdata, msg)
            return
        self.on_powerplan(ts)

    def on_powerplan(self, ts_utc_now: float) -> None:
        """Apply the power plan. Check if the relay needs to be switched on or off.
        The relay is switched on if the current temperature is below the maximum
        temperature and the current time is within the heating plan. The relay is switched off
        if the current temperature is above the maximum temperature or the current time is outside.

        Args:
            ts_utc_now (float): utc time
        """

        # optimization, check only once a minute
        elapsed: float = ts_utc_now - self.relay_started_ts
        if elapsed < 60:
            return
        self.relay_started_ts = ts_utc_now

        if not self.ranked_spot_prices:
            self.debug(f"{self.name} waiting  spot prices...", "")
            return

        if not self.power_plan:
            self.power_plan = self.create_power_plan()
            self.heating_plan = []
            self.info(
                f"{self.name} power plan of length {len(self.power_plan)} created",
                str(self.power_plan),
            )

        if not self.power_plan:
            self.error(f"{self.name} failed to create a power plan", "")
            return

        if len(self.power_plan) < 3:
            self.warning(
                f"{self.name} has suspiciously short {len(self.power_plan)}  power plan, waiting for more data ..",
                "",
            )
            self.heating_plan = []
            self.power_plan = []
            return

        if not self.ranked_solarpower or len(self.ranked_solarpower) < 4:
            self.warning(
                f"{self.name} short of forecast {len(self.ranked_solarpower)}, optimization compromised..",
                "",
            )

        if not self.heating_plan:
            self.heating_plan = self.create_heating_plan()
            if not self.heating_plan:
                self.error(f"{self.name} failed to create heating plan")
                return
            else:
                self.info(
                    f"{self.name} heating plan of length {len(self.heating_plan)} created",
                    "",
                )
        if len(self.heating_plan) < 3:
            self.warning(
                f"{self.name} has too short heating plan {len(self.heating_plan)}, no can do",
                "",
            )
            self.heating_plan = []
            self.power_plan = []
            return

        relay: int = self.consider_heating(ts_utc_now)
        if self.current_relay_state != relay:
            heat: dict[str, Any] = {
                "Unit": self.name,
                "Timestamp": ts_utc_now,
                "State": relay,
            }
            self.publish(self.topic_out_power, json.dumps(heat), 1, False)
            self.info(
                f"{self.name} relay changed to {relay} at {timestampstr(ts_utc_now)}",
                "",
            )
            self.current_relay_state = relay

    def on_netenergy_balance(self, m: dict[str, Any]) -> None:
        """Check when there is enough energy available for the radiator to heat
        in the remaining time within the balancing interval.

        Args:
            ts (float): current time

        Returns:
            bool: true if production exceeds the consumption
        """
        if m["Unit"] == self.name:
            self.net_energy_balance_mode = m["Mode"]

    def consider_heating(self, ts: float) -> int:
        """Consider whether the target boiler needs heating. Check first if the solar
        energy is enough to heat the water the remaining time in the current slot.
        If not, follow the predefined heating plan computed earlier based on the cheapest spot prices.

        Args:
            ts (float): current UTC time

        Returns:
            int: 1 if heating is needed, 0 if not
        """

        # check if we have excess energy to spent within the current slot
        if self.net_energy_balance_mode:
            self.debug(
                f"{self.name} with positive net energy balance, spend it for heating"
            )
            return 1

        hour = timestamp_hour(ts)
        state: int = -1

        # check if we are within the heating plan and see what the plan says
        for pp in self.heating_plan:
            ppts: float = pp["Timestamp"]
            h: float = timestamp_hour(ppts)
            if h == hour:
                state = pp["State"]
                break

        if state == -1:
            self.error(f"{self.name} cannot find heating plan for hour {hour}")
            return 0

        min_temp, max_temp = self.get_temperature_limits_for_current_month()
        self.debug(
            f"{self.name} month's temperature limits: Min = {min_temp}°C, Max = {max_temp}°C"
        )

        # don't heat if the current temperature is already high enough
        if self.current_temperature > max_temp:
            self.debug(
                f"{self.name} plan {state}, temp {self.current_temperature}°C already beyond max {max_temp}°C"
            )
            return 0
        #  heat if the current temperature is below the required minimum
        if self.current_temperature < min_temp:
            self.debug(
                f"{self.name} plan {state}, temp {self.current_temperature}°C below min {min_temp}°C"
            )
            return 1

        return state  # 1 = heating, 0 = not heating

    # compute utilization optimization index
    def compute_uoi(
        self,
        price: float,
        hour: float,
    ) -> float:
        """Compute UOI - utilization optimization index.

        Args:
            price (float): effective price for this device
            hour  (float) : the hour of the day

        Returns:
            float: utilization optimization index
        """

        if not is_hour_within_schedule(
            hour, self.schedule_start_hour, self.schedule_stop_hour
        ):
            return 0.0

        if price < 0.0001:
            return 1.0  # use
        elif price > self.expected_average_price:
            return 0.0  # try not to use
        else:
            fom = self.expected_average_price / price
            return fom

    def compute_effective_price(
        self, requested_power: float, available_solpower: float, spot: float
    ) -> float:
        """Compute effective electricity price. If there is enough solar power then
        electricity price is zero.

        Args:
            requested_power (float): requested power
            available_solpower (float): current solar power forecast
            spot (float): spot price
            hour  (float) : the hour of the day

        Returns:
            float: effective price for the requested power
        """

        # if we have enough solar power, use it
        if requested_power < available_solpower:
            return 0.0

        # check how  much of the power is solar and how much is from the grid
        solar_factor: float = available_solpower / requested_power

        effective_spot: float = spot * (1 - solar_factor)

        return effective_spot

    def create_power_plan(self) -> list[dict[Any, Any]]:
        """Create power plan.

        Returns:
            list: list of utilization entries
        """
        ts_utc_quantized = quantize(3600, timestamp() - 3600)
        starts: str = timestampstr(ts_utc_quantized)
        self.info(
            f"{self.name} created power plan starting at {starts} with {len(self.ranked_spot_prices)} hours of spot prices",
            "",
        )

        # syncronize spot and solarenergy by timestamp
        spots: list[dict[Any, Any]] = []
        for s in self.ranked_spot_prices:
            if s["Timestamp"] > ts_utc_quantized:
                spots.append(
                    {"Timestamp": s["Timestamp"], "PriceWithTax": s["PriceWithTax"]}
                )

        if len(spots) == 0:
            self.info(
                f"No spot prices initialized yet, can't proceed",
                "",
            )
            return []
        self.info(
            f"Have spot prices for the next {len(spots)} hours",
            "",
        )
        powers: list[dict[str, Any]] = []
        for s in self.ranked_solarpower:
            if s["ts"] >= ts_utc_quantized:
                powers.append({"Timestamp": s["ts"], "Solarenergy": s["solarenergy"]})

        num_powers: int = len(powers)
        if num_powers == 0:
            self.debug(
                f"No solar forecast initialized yet, proceed without solar forecast",
                "",
            )
        else:
            self.debug(
                f"Have solar forecast  for the next {num_powers} hours",
                "",
            )
        hplan: list[dict[str, Any]] = []
        hour: float = 0
        if len(powers) >= 8:  # at least 8 hours of solar energy forecast
            for spot, solar in zip(spots, powers):
                ts = spot["Timestamp"]
                solarenergy = solar["Solarenergy"] * 1000  # argh, this is in kW
                spotprice = spot["PriceWithTax"]
                effective_price: float = self.compute_effective_price(
                    self.radiator_power, solarenergy, spotprice
                )
                hour = timestamp_hour_local(ts, self.timezone)
                fom = self.compute_uoi(spotprice, hour)
                plan: dict[str, Any] = {
                    "Timestamp": ts,
                    "FOM": fom,
                    "Spot": effective_price,
                }
                hplan.append(plan)
        else:  # no solar forecast available, assume no free energy available
            for spot in spots:
                ts = spot["Timestamp"]
                solarenergy = 0.0
                spotprice = spot["PriceWithTax"]
                effective_price = spotprice  # no free energy available
                hour = timestamp_hour_local(ts, self.timezone)
                fom = self.compute_uoi(effective_price, hour)
                plan = {
                    "Timestamp": spot["Timestamp"],
                    "FOM": fom,
                    "Spot": effective_price,
                }
                hplan.append(plan)

        shplan = sorted(hplan, key=lambda x: x["FOM"], reverse=True)

        self.debug(f"{self.name} powerplan starts {starts} up to {len(shplan)} hours")
        return shplan

    def enable_relay(
        self, hour: float, spot: float, fom: float, end_hour: float
    ) -> bool:
        return (
            hour >= self.start_hour
            and hour < end_hour
            and float(spot) < self.spot_limit
            and fom > self.uoi_threshold
        )

    def create_heating_plan(self) -> list[dict[str, Any]]:
        """Create heating plan.

        Returns:
            int: list of heating entries
        """

        state = 0
        heating_plan: list[dict[str, Any]] = []
        hour: int = 0
        for hp in self.power_plan:
            ts: float = hp["Timestamp"]
            fom = hp["FOM"]
            spot = hp["Spot"]
            end_hour: float = self.start_hour + self.heating_hours_per_day
            local_hour: float = timestamp_hour_local(ts, self.timezone)
            schedule_on: bool = is_hour_within_schedule(
                local_hour, self.schedule_start_hour, self.schedule_stop_hour
            )

            if self.enable_relay(hour, spot, fom, end_hour) and schedule_on:
                state = 1
            else:
                state = 0
            heat: dict[str, Any] = {
                "Unit": self.name,
                "Timestamp": ts,
                "State": state,
                "Schedule": schedule_on,
                "UOI": fom,
                "Spot": spot,
            }

            self.publish(self.topic_powerplan, json.dumps(heat), 1, False)
            heating_plan.append(heat)
            hour = hour + 1

        self.info(f"{self.name} heating plan of {len(heating_plan)} hours created", "")
        return heating_plan
