import json
from typing import Any, Dict
from typing_extensions import override

from masterpiece.mqtt import MqttMsg
from juham_core import JuhamTs
from juham_core.timeutils import epoc2utc


class PowerMeterTs(JuhamTs):
    """Power meter recorder.

    Listens 'powerconsumption' topic and records the corresponding
    time series.
    """

    def __init__(self, name: str = "powermeter_record") -> None:
        super().__init__(name)
        self.power_topic = self.make_topic_name("powerconsumption")  # topic to listen

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.power_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        super().on_message(client, userdata, msg)
        if msg.topic == self.power_topic:
            m = json.loads(msg.payload.decode())
            self.record_power(m)

    def record_power(self, em: dict[str, Any]) -> None:
        """Write from the power (energy) meter to the time
        series database accordingly.

        Args:
            ts (float): utc time
            em (dict): energy meter message
        """
        point = (
            self.measurement("powermeter")
            .tag("sensor", "em0")
            .field("real_A", em["real_a"])
            .field("real_B", em["real_b"])
            .field("real_C", em["real_c"])
            .field("total_real_power", em["real_total"])
            .time(epoc2utc(em["timestamp"]))
        )
        try:
            self.write(point)
        except Exception as e:
            self.error(f"Writing to influx failed {str(e)}")

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = super().to_dict()
        data["_powermeter_record"] = {
            "power_topic": self.power_topic,
        }
        return data

    def from_dict(self, data: Dict[str, Any]) -> None:
        super().from_dict(data)
        if "_powermeter_record" in data:
            for key, value in data["_powermeter_record"].items():
                setattr(self, key, value)
