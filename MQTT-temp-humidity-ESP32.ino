
/*********
  Modified from an example from:
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_AHTX0.h>
#include <Adafruit_Sensor.h>
#include "esp_system.h"

#define uS_TO_S_FACTOR 1000000  /* Conversion factor for micro seconds to seconds */
#define TIME_TO_SLEEP  60        /* Time ESP32 will go to sleep (in seconds) */

RTC_DATA_ATTR int bootCount = 0;

const int wdtTimeout = 70000;  /* time in ms to trigger the watchdog This should be 70 seconds.
                                  10 seconds longer than loop count. */
hw_timer_t *timer = NULL;

void IRAM_ATTR resetModule() {  /* ISR for watchdog timer.  If it goes off, reset the system */
  esp_restart();
}

// Replace the next variables with your SSID/Password combination
const char* ssid = "your SSID";
const char* password = "your WPA passphrase";

// Add your MQTT Broker IP address, example:
const char* mqtt_server = "192.168.1.25";
int status = WL_CONNECTED;

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
char msg[50];
int value = 0;

Adafruit_AHTX0 aht; // I2C

float temperature = 0;
float humid = 0;

void setup_wifi() {
  
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  delay(100);
  status = WiFi.begin(ssid, password);
  while (status != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
    status = WiFi.status();
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client1")) {
      Serial.println("connected");
    }
      
   else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      // Wait 2 seconds before retrying
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000); //Take some time to open up the Serial Monitor
  
  /* setup watchdog timer */
  
  timer = timerBegin(0, 80, true);
  timerAttachInterrupt(timer, &resetModule, true);
  timerAlarmWrite(timer, wdtTimeout * 1000, false);
  timerAlarmEnable(timer);
  
  //Increment boot number and print it every reboot
  ++bootCount;
  Serial.println("\nBoot number: " + String(bootCount));

  //status = aht.begin();  
  if (!aht.begin()) {
    Serial.println("Could not find a valid AHT20 sensor, check wiring!");
    while (1);
  }
 
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  if (!client.connected()) {
    reconnect();
  }

  sensors_event_t humidity, temp;
  aht.getEvent(&humidity, &temp);// populate temp and humidity objects with fresh data
  
  temperature = 1.8 * temp.temperature + 32.0; // Temperature in Fahrenheit
  humid = humidity.relative_humidity;
    
  // Convert the value to a char array
  char tempString[8];
  dtostrf(temperature, 1, 1, tempString);
  // Convert the value to a char array
  char humString[8];
  dtostrf(humid, 1, 1, humString);
  
// The data format is set to work with influxDB. It's an array of objects.
//    1st object is temp and humidity. 2nd object is location of the reading and is treated as a KEY
// Same principle for loop count and it's location.  Loop count is a debug aid to see how often the WDT fires

  const char datastr1[20] = "[{\"Temperature\": ";
  char buf[100] = "";
  strcat(buf, datastr1);
  strcat(buf, tempString);
  const char datastr2[20] = " , \"Humidity\": ";
  strcat(buf, datastr2);
  strcat(buf, humString);
  const char locationString[32] = "}, {\"Location\": \"basement\"}]";
  strcat(buf, locationString);
  Serial.println(buf);
  client.publish("environmentTopic", buf);

  // post loop count
  char loopString[20];
  dtostrf(bootCount, 1, 0, loopString);
  const char datastr7[21] = "[{\"Loop Count\": ";
  strcpy(buf,"");
  strcat(buf, datastr7);
  strcat(buf, loopString);

  strcat(buf, locationString);
  Serial.println(buf);
  client.publish("environmentTopic", buf);

  esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP * uS_TO_S_FACTOR);
  Serial.println("Setup ESP32 to sleep for every " + String(TIME_TO_SLEEP) +
  " Seconds");

  Serial.println("Going to sleep now\n");
  delay(1000);
  Serial.flush(); 
  esp_deep_sleep_start();
}

void loop() {
    //This is not going to be called
}
