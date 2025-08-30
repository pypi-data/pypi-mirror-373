from datetime import datetime
import time
import json
from typing import Any, Dict, Optional, cast
from typing_extensions import override

from masterpiece.mqtt import Mqtt, MqttMsg
from juham_core.timeutils import epoc2utc
from juham_core import JuhamTs


class ElectricityPriceTs(JuhamTs):
    """Spot electricity price for reading hourly electricity prices from"""

    def __init__(self, name: str = "electricityprice_ts") -> None:
        super().__init__(name)

        self.spot_topic = self.make_topic_name("spot")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.spot_topic)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        if msg.topic == self.spot_topic:
            em = json.loads(msg.payload.decode())
            self.on_spot(em)
        else:
            super().on_message(client, userdata, msg)

    def on_spot(self, m: dict[Any, Any]) -> None:
        """Write hourly spot electricity prices to time series database.

        Args:
            m (dict): holding hourlys spot electricity prices
        """
        grid_cost : float
        for h in m:
            if "GridCost" in h:
                grid_cost = h["GridCost"]
                point = (
                    self.measurement("spot")
                    .tag("hour", h["Timestamp"])
                    .field("value", h["PriceWithTax"])
                    .field("grid", grid_cost)
                    .time(epoc2utc(h["Timestamp"]))
                )
                self.write(point)
