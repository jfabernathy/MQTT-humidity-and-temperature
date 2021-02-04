# this is the python program for Raspberry Pi OS
# It has been tested on a RPI 3
#
import paho.mqtt.client as mqtt  # Import the MQTT library
import json
import time  # The time library is useful for delays
import board

import adafruit_ahtx0

# Create the sensor object using I2C
sensor = adafruit_ahtx0.AHTx0(board.I2C())

tempHumidity = {"Temperature": "placeholder", "Humidity": "placeholder"}


ourClient = mqtt.Client()  # Create a MQTT client object

ourClient.connect("192.168.0.25", 1883)  # Connect to the test MQTT broker

ourClient.loop_start()  # Start the MQTT client

# Main program loop

while 1:
    x = round(sensor.temperature * 1.8 + 32.0, 1)
    tempHumidity["Temperature"] = x
    x = round(sensor.relative_humidity, 1)
    tempHumidity["Humidity"] = x
    y = json.dumps(tempHumidity)
    y = "[" + y + """,{"Location": "RV"}]"""

    ourClient.publish("environmentTopic", y)  # Publish message to MQTT broker

    time.sleep(60)  # Sleep for 60 seconds
