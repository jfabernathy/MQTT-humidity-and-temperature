import time
import terminalio
from adafruit_magtag.magtag import MagTag

months = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

USE_24HR_TIME = False

# Set up data location and fields
DATA_SOURCE = "http://192.168.0.25:1880/5th_wheel"

reading_time = ["time"]
reading_Temperature = ["Temperature"]
reading_Humidity = ["Humidity"]

# These functions take the JSON data keys and does checks to determine
#   how to display the data. They're used in the add_text blocks below

def Temperature_transform(val3):
    if val3 == None:
        val3 = "Unavailable"
    return "Temperature: " + str(val3)

def time_transform(val):
    if val == None:
        val = "When: Unavailable"
    month = int(val[5:7])
    day = int(val[8:10])
    hour = int(val[11:13]) - 5
    if hour < 0:
        hour = hour + 24
        day = day -1
    min = int(val[14:16])

    if USE_24HR_TIME:
        timestring = "%d:%02d" % (hour, min)
    elif hour > 12:
        timestring = "%d:%02d pm" % (hour-12, min)
    else:
        timestring = "%d:%02d am" % (hour, min)

    return "%s %d, at %s" % (months[month-1], day, timestring)

def Humidity_transform(val2):
    if val2 == None:
        return "Details: To Be Determined"
    return "Humidity: " + str(val2)

# Set up the MagTag with the JSON data parameters
magtag = MagTag(
    url=DATA_SOURCE,
    json_path=(reading_time, reading_Temperature, reading_Humidity)
)

magtag.add_text(
    text_font="/fonts/Lato-Bold-ltd-25.bdf",
    text_position=(10, 15),
    is_data=False
)
# Display heading text below with formatting above
magtag.set_text("5th Wheel")

# Formatting for the Time text
magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_position=(10, 38),
    text_transform=time_transform
)

# Formatting for the Temperature text
magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_position=(10, 60),
    text_transform=Temperature_transform
)

# Formatting for the Humidity text
magtag.add_text(
    text_font="/fonts/Arial-12.bdf",
    text_position=(10, 82),
    text_transform=Humidity_transform
)

try:
    # Have the MagTag connect to the internet
    magtag.network.connect()
    # This statement gets the JSON data and displays it automagically
    value = magtag.fetch()
    print("Response is", value)
except (ValueError, RuntimeError) as e:
    print("Some error occured, retrying! -", e)

# wait 2 seconds for display to complete
time.sleep(2)
magtag.exit_and_deep_sleep(60 * 5)