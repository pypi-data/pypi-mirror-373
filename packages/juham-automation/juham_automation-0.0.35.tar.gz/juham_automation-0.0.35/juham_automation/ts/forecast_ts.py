import json
from typing import Any
from typing_extensions import override

from masterpiece.mqtt import MqttMsg
from juham_core import JuhamTs
from juham_core.timeutils import epoc2utc


class ForecastTs(JuhamTs):
    """Forecast database record.

    This class listens the forecast topic and writes to the time series
    database.
    """

    def __init__(self, name: str = "forecast_ts") -> None:
        """Construct forecast record object with the given name."""
        super().__init__(name)
        self.forecast_topic = self.make_topic_name("forecast")

    @override
    def on_connect(self, client: object, userdata: Any, flags: int, rc: int) -> None:
        """Standard mqtt connect notification.

        This method is called when the client connection with the MQTT
        broker is established.
        """
        super().on_connect(client, userdata, flags, rc)
        self.subscribe(self.forecast_topic)
        self.debug(f"Subscribed to {self.forecast_topic}")

    @override
    def on_message(self, client: object, userdata: Any, msg: MqttMsg) -> None:
        """Standard mqtt message notification method.

        This method is called upon new arrived message.
        """
        if msg.topic == self.forecast_topic:
            m = json.loads(msg.payload.decode())
            self.on_forecast(m)
        else:
            super().on_message(client, userdata, msg)

    def on_forecast(self, em: dict[Any, Any]) -> None:
        """Handle weather forecast data. Writes the received hourly forecast
        data to timeseries database.

        Args:
            em (dict): forecast
        """

        # List of fields you want to add
        fields = [
            "ts",
            "day",
            "solarradiation",
            "solarenergy",
            "cloudcover",
            "snowdepth",
            "uvindex",
            "pressure",
            "humidity",
            "windspeed",
            "winddir",
            "temp",
            "feels",
        ]
        days: int = 0
        for m in em:
            senderid: str = "unknown"
            if "id" in m:
                senderid = m["id"]
            if not "hour" in m:
                self.error(
                    f"No hour key in forecast record from {senderid}, skipped", str(m)
                )
            else:
                point = (
                    self.measurement("forecast")
                    .tag("hour", m.get("hour"))
                    .tag("source", senderid)
                    .field("hr", str(m["hour"]))
                )
                # Conditionally add each field
                for field in fields:
                    if field in m:
                        if field == "day" or field == "ts":
                            point = point.field(field, m[field])
                        else:
                            point = point.field(field, float(m[field]))
                    point = point.time(epoc2utc(m["ts"]))
                self.write(point)
                days = days + 1
        self.info(
            f"Forecast from {senderid} for the next {days} days written to time series database"
        )
