import json
from typing import Any, Dict, cast
from typing_extensions import override

from masterpiece.mqtt import MqttMsg
from juham_core import Juham
from juham_core.timeutils import timestamp
from juham_core import MasterPieceThread, JuhamThread


class PowerMeterSimulatorThread(MasterPieceThread):
    """Thread simulating Energy Meter."""

    _power: float = 1000.0  # W
    _power_topic: str = "power"
    _interval: float = 10  # 10 seconds

    def __init__(self) -> None:
        """Construct a thread for publishing power data.

        Args:
            topic (str, optional): MQTT topic to post the sensor readings. Defaults to None.
            interval (float, optional): Interval specifying how often the sensor is read. Defaults to 60 seconds.
        """
        super().__init__(None)
        self.current_ts: float = timestamp()

    @classmethod
    def initialize(cls, power_topic: str, power: float, interval: float) -> None:
        """Initialize thread  class attributes.

        Args:
            power_topic (str): topic to publish the energy meter readings
            power (float): power  to be simulated, the default is 1kW
            interval (float): update interval, the default is 10s
        """
        cls._power = power
        cls._interval = interval
        cls._power_topic = power_topic

    @override
    def update_interval(self) -> float:
        return self._interval

    def publish_active_power(self, ts: float) -> None:
        """Publish the active power, also known as real power. This is that
        part of the  power that can be converted to useful work.

        Args:
            ts (str): time stamp of the event

        """
        dt = ts - self.current_ts
        self.current_ts = ts

        msg = {
            "timestamp": ts,
            "real_a": self._power * dt,
            "real_b": self._power * dt,
            "real_c": self._power * dt,
            "real_total": 3 * self._power * dt,
        }
        self.publish(self._power_topic, json.dumps(msg), 1, True)

    @override
    def update(self) -> bool:
        super().update()
        self.publish_active_power(timestamp())
        return True


class PowerMeterSimulator(JuhamThread):
    """Simulator energy meter sensor. Spawns a thread
    to simulate Shelly PM mqtt messages"""

    workerThreadId = PowerMeterSimulatorThread.get_class_id()
    update_interval: float = 10
    power: float = 1000.0

    _POWERMETERSIMULATOR: str = "_powermetersimulator"

    def __init__(
        self,
        name: str = "em",
        interval: float = 0,
    ) -> None:
        """Create energy meter simulator.

        Args:
            name (str, optional): Name of the object. Defaults to 'em'.
            topic (str, optional): MQTT topic to publish the energy meter reports. Defaults to None.
            interval (float, optional): interval between events, in seconds. Defaults to None.
        """
        super().__init__(name)
        self.update_ts: float = 0.0
        if interval > 0.0:
            self.update_interval = interval
        self.power_topic = self.make_topic_name("powerconsumption")  # target topic

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.power_topic:
            em = json.loads(msg.payload.decode())
            self.on_sensor(em)
        else:
            super().on_message(client, userdata, msg)

    def on_sensor(self, em: dict[Any, Any]) -> None:
        """Handle data coming from the energy meter.

        Simply log the event to indicate the presense of simulated device.
        Args:
            em (dict): data from the sensor
        """
        self.debug(f"Simulated power meter sensor {em}")

    @override
    def run(self) -> None:
        PowerMeterSimulatorThread.initialize(
            self.power_topic, self.power, self.update_interval
        )
        self.worker = cast(
            PowerMeterSimulatorThread,
            Juham.instantiate(PowerMeterSimulatorThread.get_class_id()),
        )
        super().run()

    @override
    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        data[self._POWERMETERSIMULATOR] = {"power_topic": self.power_topic}
        return data

    @override
    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        if self._POWERMETERSIMULATOR in data:
            for key, value in data[self._POWERMETERSIMULATOR].items():
                setattr(self, key, value)
