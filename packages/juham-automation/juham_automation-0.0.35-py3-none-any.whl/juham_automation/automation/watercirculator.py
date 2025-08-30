from typing import Any
from typing_extensions import override
import json

from masterpiece.mqtt import MqttMsg
from juham_core import Juham
from juham_core.timeutils import timestamp


class WaterCirculator(Juham):
    """Hot Water Circulation Automation

    This system monitors motion sensor data to detect home occupancy.

    - **When motion is detected**: The water circulator pump is activated, ensuring hot water is
        instantly available when the tap is turned on.
    - **When no motion is detected for a specified period (in seconds)**: The pump automatically
        switches off to conserve energy.

    Future improvement idea
    ------------------------

    In cold countries, such as Finland, energy conservation during the winter season may not be a priority.
    In this case, an additional temperature sensor measuring the outside temperature could be used to determine whether
    the circulator should be switched off at all. The circulating water could potentially act as an additional heating radiator.

    Points to consider
    ------------------

    - Switching the pump on and off may affect its lifetime.
    - Keeping the pump running with hot water could impact the lifespan of the pipes, potentially causing
      corrosion due to constant hot water flow.

    """

    uptime = 60 * 60  # one hour
    min_temperature = 37

    def __init__(self, name: str, temperature_sensor: str) -> None:
        super().__init__(name)

        # input topics
        self.motion_topic = self.make_topic_name("motion")  # motion detection
        self.temperature_topic = self.make_topic_name(temperature_sensor)

        # relay to be controlled
        self.topic_power = self.make_topic_name("power")

        # for the pump controlling logic
        self.current_motion: bool = False
        self.relay_started_ts: float = 0
        self.water_temperature: float = 0
        self.water_temperature_updated: float = 0
        self.initialized = False

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.motion_topic)
            self.subscribe(self.temperature_topic)
            # reset the relay to make sure the initial state matches the state of us
            self.publish_relay_state(0)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.temperature_topic:
            m = json.loads(msg.payload.decode())
            self.on_temperature_sensor(m, timestamp())
        elif msg.topic == self.motion_topic:
            m = json.loads(msg.payload.decode())
            self.on_motion_sensor(m, timestamp())
        else:
            super().on_message(client, userdata, msg)

    def on_temperature_sensor(self, m: dict[str, Any], ts_utc_now: float) -> None:
        """Handle message from the hot water pipe temperature sensor.
        Records the temperature and updates the water_temperature_updated attribute.

        Args:
            m (dict): temperature reading from the hot water blump sensor
            ts_utc_now (float): _current utc time
        """

        self.water_temperature = m["temperature"]
        self.water_temperature_updated = ts_utc_now
        # self.info(
        #    f"Temperature of circulating water updated to {self.water_temperature} C"
        # )

    def on_motion_sensor(self, m: dict[str, dict[str, Any]], ts_utc_now: float) -> None:
        """Control the water cirulator bump.

        Given message from the motion sensor consider switching the
        circulator bump on.

        Args:
            msg (dict): directionary holding motion sensor data
            ts_utc_now (float): current time stamp
        """
        sensor = m["sensor"]
        vibration: bool = bool(m["vibration"])
        motion: bool = bool(m["motion"])

        if motion or vibration:
            # self.debug(f"Life form detected in {sensor}")
            # honey I'm home
            if not self.current_motion:
                if self.water_temperature > self.min_temperature:
                    self.publish_relay_state(0)
                    # self.debug(
                    #    f"Circulator: motion detected but water warm already {self.water_temperature} > {self.min_temperature} C"
                    # )
                else:
                    self.current_motion = True
                    self.relay_started_ts = ts_utc_now
                    self.publish_relay_state(1)
                    self.initialized = True
                    self.info(
                        f"Circulator pump started, will run for {int(self.uptime / 60)} minutes "
                    )
            else:
                self.publish_relay_state(1)
                self.relay_started_ts = ts_utc_now
                # self.debug(
                #    f"Circulator pump has been running for {int(ts_utc_now - self.relay_started_ts)/60} minutes",
                #    " ",
                # )
        else:
            if self.current_motion or not self.initialized:
                elapsed: float = ts_utc_now - self.relay_started_ts
                if elapsed > self.uptime:
                    self.publish_relay_state(0)
                    self.info(
                        f"Circulator  pump stopped, no motion in {int(elapsed/60)} minutes detected",
                        "",
                    )
                    self.current_motion = False
                    self.initialized = True
                else:
                    self.publish_relay_state(1)
                    # self.debug(
                    #    f"Circulator bump stop countdown {int(self.uptime - (ts_utc_now - self.relay_started_ts ))/60} min"
                    # )
            else:
                self.publish_relay_state(0)
                # self.debug(
                #    f"Circulator bump off already, temperature {self.water_temperature} C",
                #    "",
                # )

    def publish_relay_state(self, state: int) -> None:
        """Publish power status.

        Args:
            state (int): 1 for on, 0 for off, as defined by Juham 'power' topic
        """
        heat = {"Unit": self.name, "Timestamp": timestamp(), "State": state}
        self.publish(self.topic_power, json.dumps(heat), 1, False)
