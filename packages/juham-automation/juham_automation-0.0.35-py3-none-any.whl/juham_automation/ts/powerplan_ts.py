import json
from typing import Any
from typing_extensions import override

from masterpiece.mqtt import MqttMsg
from juham_core import JuhamTs
from juham_core.timeutils import epoc2utc


class PowerPlanTs(JuhamTs):
    """Power plan time series record.

    Listens powerplan topic and updates time series database
    accordingly.
    """

    def __init__(self, name: str = "powerplan_ts") -> None:
        super().__init__(name)
        self.powerplan_topic = self.make_topic_name("powerplan")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        self.subscribe(self.powerplan_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        super().on_message(client, userdata, msg)
        m = json.loads(msg.payload.decode())
        schedule = m["Schedule"]
        uoi = m["UOI"]
        ts = m["Timestamp"]

        point = (
            self.measurement("powerplan")
            .tag("unit", m["Unit"])
            .field("state", m["State"])  # 1 on, 0 off
            .field("name", m["Unit"])  # e.g main_boiler
            .field("type", "C")  # C=consumption, S = supply
            .field("power", 16.0)  # kW
            .field("Schedule", schedule)  # figures of merit
            .field("UOI", float(uoi))  # Utilitzation Optimizing Index
            .time(epoc2utc(ts))
        )
        self.write(point)
