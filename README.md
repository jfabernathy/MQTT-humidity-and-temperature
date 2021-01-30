# MQTT-humidity-and-temperature
This program is a temperature and humidity logging program for use in collection the data once a minute and posting via WiFi using the MQTT protcol.
The hardware collecting the data is an Adafruit ESP32 Feather Huzzah MCU board and an Adafruit AHT20 Temperature and Humidity I2C sensor board.
It's part of a system where the agent collecting the data is a Raspberry Pi 4 in my case running a Docker container system with the following:
  Mosquitto MQTT Broker
  NodeRed 
  influxDB database
  grafana for charting
The RPI4 and the ESP32 board are on the same network. The ESP32 is fairly remote and error correction for WiFi failure in included.
The data format posted by the ESP32 is in a format that works for influxDB which is a Array of objects. The first object is the environment data and the 2nd object is the location. This allows for multiple MCUs in different location.
An example of the data is [{"Temperature": 72.0, "Humidity": 40.1}, {"Location": "basement"}]
