import json
from typing import Any
from typing_extensions import override

from masterpiece.mqtt import MqttMsg

from juham_core import JuhamTs
from juham_core.timeutils import epoc2utc


class EnergyBalancerTs(JuhamTs):
    """Record energy balance data to time series database.

    This class listens the "energybalance" MQTT topic and records the
    messages to time series database.
    """

    def __init__(self, name: str = "energybalancer_ts") -> None:
        """Construct record object with the given name."""

        super().__init__(name)
        self.topic_in_status = self.make_topic_name("energybalance/status")
        self.topic_in_diagnostics = self.make_topic_name("energybalance/diagnostics")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_in_status)
            self.subscribe(self.topic_in_diagnostics)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.topic_in_status:
            self.on_status(json.loads(msg.payload.decode()))
        elif msg.topic == self.topic_in_diagnostics:
            self.on_diagnostics(json.loads(msg.payload.decode()))
        else:
            super().on_message(client, userdata, msg)

    def on_status(self, m: dict[str, Any]) -> None:
        """Handle energybalance message.
        Args:
            m (dict[str, Any]): Message from energybalance topic.
        """
        if not "Power" in m or not "Timestamp" in m:
            self.error(f"INVALID STATUS msg {m}")            
            return
        point = (
            self.measurement("energybalance")
            .tag("Unit", m["Unit"])
            .field("Mode", m["Mode"])
            .field("Power", float(m["Power"]))
            .time(epoc2utc(m["Timestamp"]))
        )
        self.write(point)

    def on_diagnostics(self, m: dict[str, Any]) -> None:
        """Handle energybalance diagnostics.
        Args:
            m (dict[str, Any]): Message from energybalance topic.
        """
        if not "Timestamp" in m:
            self.error(f"INVALID DIAGNOSTICS msg {m}")
            return
        point = (
            self.measurement("energybalance")
            .tag("EnergyBalancer", m["EnergyBalancer"])
            .field("CurrentBalance", m["CurrentBalance"])
            .field("NeededBalance", m["NeededBalance"])
            .time(epoc2utc(m["Timestamp"]))
        )
        self.write(point)
