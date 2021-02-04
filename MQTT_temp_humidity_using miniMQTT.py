import socketpool
import ssl
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import wifi
import time
import board
import adafruit_ahtx0
import alarm
import busio

PUBLISH_DELAY = 60
MQTT_TOPIC = "environmentTopic"
USE_DEEP_SLEEP = True

from microcontroller import watchdog as w
from watchdog import WatchDogMode
w.timeout=70 # Set a timeout of 70 seconds
w.mode = WatchDogMode.RESET
w.feed()

def alarm_deepSleep(how_long):
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + how_long)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

def debug_log(msg):
    uart.write(bytearray("\n\r" + msg))
    print(msg)

def post_data(msg):
    try:
        mqtt_client.connect()
        mqtt_client.publish(MQTT_TOPIC, msg)
        mqtt_client.disconnect()
    except Exception as e:
        print("Exception in post_data ", str(e))
        uart.write(bytearray("\n\rException in post_data " + str(e)))
        alarm_deepSleep(2)

w.timeout=70 # Set a timeout of 70 seconds
w.mode = WatchDogMode.RESET
w.feed()

# Create the sensor object using I2C
sensor = adafruit_ahtx0.AHTx0(board.I2C())

from adafruit_lc709203f import LC709203F
sensor2 = LC709203F(board.I2C())

uart = busio.UART(board.TX, board.RX, baudrate=115200)

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

debug_log("Connecting to %s"%secrets["ssid"])

try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
except Exception as e:
    print("Exception on wifi.radio.connect ", str(e))
    uart.write(bytearray("\n\rError on wifi.radio.connect " + str(e)))
    alarm_deepSleep(2)

debug_log("Connected to %s!"%secrets["ssid"])

debug_log("My IP address is " + str(wifi.radio.ipv4_address))

# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["mqtt_broker"],
    port=secrets["mqtt_port"],
    username=secrets["mqtt_username"],
    password=secrets["mqtt_password"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

x = round(sensor.temperature * 1.8 + 32.0, 1)
y = round(sensor.relative_humidity, 1)
temp = str(x)
humid = str(y)

cell_voltage = str(sensor2.cell_voltage)
cell_percent = str(sensor2.cell_percent)

# format the readings data as  InfluxDB expects: Array of 2 object:
# 1st is readings, 2nd is tag

data = """[{"Temperature": """ + temp + """ , "Humidity": """ + humid + """}, {"Location": "RV_basement"}]"""
post_data(data)

loop_count = alarm.sleep_memory[5] | alarm.sleep_memory[6] << 8
loop_count += 1
alarm.sleep_memory[6] = loop_count >> 8
alarm.sleep_memory[5] = loop_count & 255

data = """[{"Battery Volts ": """ + cell_voltage + """ , "Battery percent": """ + cell_percent + """, "Loop count": """ + str(loop_count) + """}, {"Location": "RV_basement"}]"""
post_data(data)

debug_log("Loop count = " + str(loop_count))

debug_log("Battery: %0.3f Volts / %0.1f %%" % (sensor2.cell_voltage, sensor2.cell_percent))

debug_log("Just posted data, now into deep sleep!\n\n")

# Create an alarm that will trigger 60 seconds from now to awake from deep sleep
alarm_deepSleep(60)