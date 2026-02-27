# SensorPush Monitor

Reads the environment variables SENSORPUSH_USER and SENSORPUSH_PASSWORD and uses those credentials to log in to the SensorPush API. It retrieves the sensors and the most current reading from the sensors, displaying them in a GUI. This data is updated every 5 minutes. If temperature limits are set and the sensor reading is outside the limit, it will display in red. Battery voltage 2.3 volts or under will display in red with a warning to replace the battery.

