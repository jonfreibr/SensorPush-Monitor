# SensorPush Monitor

Reads the environment variables SENSORPUSH_USER and SENSORPUSH_PASSWORD and uses those credentials to log in to the SensorPush API. It retrieves the sensors and the most current reading from the sensors, displaying them in a GUI. This data is updated every minute. If temperature limits are set and the sensor reading is outside the limit, it will display in red if over the limit and blue if under the limit. Battery voltage 2.3 volts or under will display in red with a warning to replace the battery.

If a temperature range is set, there needs to be both a high and a low limit. "Alert Me" must also be selected.

pysensorpush module license: Apache 2.0 License (http://www.apache.org/licenses/LICENSE-2.0)
