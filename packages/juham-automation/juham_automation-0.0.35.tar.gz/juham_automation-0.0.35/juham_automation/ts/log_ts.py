import json
from typing import Any
from typing_extensions import override

from masterpiece.mqtt import MqttMsg
from juham_core import JuhamTs
from juham_core.timeutils import epoc2utc


class LogTs(JuhamTs):
    """Class recording application events, such as warnings and errors,
    to time series database."""

    def __init__(self, name: str = "log_ts") -> None:
        """Creates mqtt client for recording log events to time series
        database.

        Args:
            name (str): name for the client
        """
        super().__init__(name)
        self.topic_name = self.make_topic_name("log")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        """Connects the client to mqtt broker.

        Args:
            client (obj): client to be connected
            userdata (any): caller specific data
            flags (int): implementation specific shit

        Returns:
            rc (bool): True if successful
        """
        super().on_connect(client, userdata, flags, rc)
        if rc == 0:
            self.subscribe(self.topic_name)

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        m = json.loads(msg.payload.decode())
        ts = epoc2utc(m["Timestamp"])

        point = (
            self.measurement("log")
            .tag("class", m["Class"])
            .field("source", m["Source"])
            .field("msg", m["Msg"])
            .field("details", m["Details"])
            .field("Timestamp", m["Timestamp"])
            .time(ts)
        )
        try:
            self.write(point)
        except Exception as e:
            self.log_message("Error", f"Cannot write log event {m['Msg']}", str(e))
