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
#   val is in format '2021-03-25T20:07:39.402Z'

    dstStart = {2021: 14, 2022: 13, 2023: 12, 2024: 10, 2025: 9, 2026: 8, 2027: 14, 2028: 12, 2029: 11, 2030: 10, 2031: 9}

    dstStop = {2021: 7, 2022: 6, 2023: 5, 2024: 3, 2025: 2, 2026: 1, 2027: 7, 2028: 5, 2029: 4, 2030: 3, 2031: 2}

    if val == None:
        val = "When: Unavailable"
    year = int(val[0:4])
    month = int(val[5:7])
    day = int(val[8:10])
    hour = int(val[11:13]) # hour is in UTC
    if month in range(3, 12):
        if month == 3 and day >= int(dstStart[year])+1 or month == 3 and day == int(dstStart[year]) and hour >= 7:
            timezoneOffset = 4

        elif month == 11 and day <= int(dstStop[year]):
            if day <= int(dstStop[year])-1 or day == int(dstStop[year]) and hour <= 6:
                timezoneOffset = 4
            else:
                timezoneOffset = 5

        elif month in range(4,11):
            timezoneOffset = 4
        else:
            timezoneOffset = 5

    else:
        timezoneOffset = 5

    hour = hour - timezoneOffset
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

    return "%s %d, %d, at %s" % (months[month-1], day, year, timestring)

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
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 38),
    text_transform=time_transform
)

# Formatting for the Temperature text
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 60),
    text_transform=Temperature_transform
)

# Formatting for the Humidity text
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(10, 82),
    text_transform=Humidity_transform
)

try:
    # Have the MagTag connect to the internet
    magtag.network.connect()
    # This statement gets the JSON data and displays it automagically
    value = magtag.fetch()
    print("Response is", value)
except Exception as e:
    print("Some error occured, retrying! -", e)
    magtag.exit_and_deep_sleep(2)
# wait 2 seconds for display to complete
time.sleep(2)
magtag.exit_and_deep_sleep(60 * 5)