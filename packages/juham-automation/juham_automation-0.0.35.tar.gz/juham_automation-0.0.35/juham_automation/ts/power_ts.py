import json
from typing import Any
from typing_extensions import override

from masterpiece.mqtt import MqttMsg

from juham_core import JuhamTs
from juham_core.timeutils import epoc2utc


class PowerTs(JuhamTs):
    """Power utilization record.

    This class listens the power utilization message and writes the
    state to time series database.
    """

    def __init__(self, name: str = "power_ts") -> None:
        """Construct power record object with the given name."""

        super().__init__(name)
        self.topic_name = self.make_topic_name("power")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        self.subscribe(self.topic_name)
        self.debug(f"Subscribed to {self.topic_name}")

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        """Standard mqtt message notification method.

        This method is called upon new arrived message.
        """

        m = json.loads(msg.payload.decode())
        if not "Unit" in m:
            return
        unit = m["Unit"]
        ts = m["Timestamp"]
        state = m["State"]
        point = (
            self.measurement("power")
            .tag("unit", unit)
            .field("state", state)
            .time(epoc2utc(ts))
        )
        self.write(point)
