# MQTT-humidity-and-temperature
This Arduino program is a temperature and humidity logging program for use in collecting the data once a minute and posting via WiFi using the MQTT protcol.
The hardware collecting the data is an Adafruit ESP32 Feather Huzzah MCU board and an Adafruit AHT20 Temperature and Humidity I2C sensor board. Other types of MCUs/CPUs have been added over time for extra location data collectors.

It's part of a system where the agent collecting the data is a Raspberry Pi 4 in my case running a Docker container system with the following:

  Mosquitto MQTT Broker
  
  NodeRed
  
  influxDB database
  
  grafana for charting

The RPI4 and the ESP32 board are on the same network. The ESP32 is fairly remote and error correction for WiFi failure in included. There is also a watchdog timer used in case the code or MCU just quits working. The WDT will just reset the system.

The data format posted by the ESP32 is in a format that works for influxDB which is a Array of objects. The first object is the environment data and the 2nd object is the location. This allows for multiple MCUs in different location.
An example of the data is:

[{"Temperature": 72.0, "Humidity": 40.1}, {"Location": "basement"}]

Because this program would run for many hours then just stop running and not post any data, it was necessary to implement a watchdog timer.  Since the loop time of postings was 60 seconds I made the WDT set for 70 seconds.
Since I'm using Deep Sleep after each posting, the code is written as a setup only, no loop. So if the MCU doesn't wake up on time or if the code is stuck somewhere, the WDT resets the board and it continues.
The WDT has been seen to work for me. If this shows not to work reliably, I'll implement an external WDT that trips the power to the MCU.

I've included the Nodered flow I used and that has both the MQTT input and one for HTTP since some of my MCUs are using circuitpython which does not have MQTT libraries at this time.

The Arduino program is intented to be used on an ESP32 board like the Adafruit ESP32 Feather Huzzah.  I'm also using a Raspberry Pi 3 to read sensors and post that data to the same server.
That RPI3 code is written in Python and and uses the MQTT libraries from https://pypi.org/project/paho-mqtt/ and I used the Adafruit Blink library (https://pypi.org/project/Adafruit-Blinka/) for the temperature and humidity sensors.

I also did a version of the application in CircuitPython for the Metro ESP32-S2 Express board from Adafruit. Since the CircuitPython libraries for MQTT were not available when I started this project, I used HTTP Post calls.  NodeRed handles both.

Once the miniMQTT library became available for CircuitPython, I also built a version of the program for that for the Metro ESP32-S2

I've included those programs.

The most recent addition is a CircuitPython program for the Adafruit Magtag e-Ink display and ESP32-S2 board. https://www.adafruit.com/product/4800
This program using the Magtag.fetch to retrieve over WiFi the most recent temperature and humidity from the influxDB for a given location and displays it on the e-Ink display.  It repeats this every 5 minutes and deep sleeps while waiting.  With the e-ink display retaining the display during deep sleep, it makes an interesting information display where the updating constantly isn't needed.  The Magtag is LiPoly battery powered and can go for days without recharging.
