## Building the Docker Containers for Environmental data collection

### Overview:

This document explains the steps I used to build the data collection system that receives the environmental data sent by remote micro controllers over WiFi. The system is built on a Raspberry Pi 4 using a Docker container system.

### Details:

I use the IOTStack system that is described at: [https://sensorsiot.github.io/IOTstack/Getting-Started/](https://sensorsiot.github.io/IOTstack/Getting-Started/)

1. Start with a clean fresh install of Raspberry Pi OS Desktop with or without recommended software.
2. From the IOTStack Getting Started webpage follow along with the steps below.
3. Run this command:

curl -fsSL https://raw.githubusercontent.com/SensorsIot/IOTstack/master/install.sh | bash

1. At the popup &quot;Docker and Docker-compose not installed and is required&quot;. default is yes, so [enter]
2. Reboot when done
3. cd ~/IOTstack
4. ./menu.sh
5. At the popup&quot;Python 3 and Dependencies&quot;, answer yes.
6. Now in the IOStack Main Menu with &quot;Build Stack&quot; highlighted (make terminal window large so you can see all of the menu)
7. Go down the list of containers hitting [space] to select the containers you want, which in this case are:

grafana

influxdb

mosquitto

nodered

poartainer-ce (Optional)

- On nodered you will see warning in orange. Use [right arrow] for options to fix.  
- With Select and build addons listed, Press enterto build addons.   
- Select go back option.  
- Back on Select Containers to Build page nodered is now marked pass with no warning.  
8. Hit [enter] to start building and [enter] on the mosquitto question about port number.
9. Exit
10. Critical part: edit docer-compose.yml
11. Make this change in influxdb section:

image: &quot;influxdb:latest&quot; to image: &quot;influxdb:1.8.4&quot;

12. We are pinning influxdb to version 1.8.4. That should be it but there are some things to be informed about. See [https://github.com/SensorsIot/IOTstack/issues/265](https://github.com/SensorsIot/IOTstack/issues/265)
13. Everything should be setup. Since we have not setup any passwords for mosquitto the mosquitto.conf should be okay.
14. Run &quot;docker-compose up -d&quot;
15. At this point the containers are built and running.
16. There is a lot to setup, like influxdb database, usernames and passwords for influxdb, grafana, and portainer. Flows for nodered, charts for grafana.
17. You get to the different containers via the web:

- you get to nodered from your RPI4 localhost:1880  
- you get to grafana from your RPI4 localhost:3000  
- you get to portainer from your RPI4 localhost:9000  

18. From other PC on local network change localhost to IP address of RPI4
19. Within the docker containers the IPs are aliased, so for example, in nodered you use the IP address **mosquitto:1883**. That&#39;s what you see in the MQTT flow node for nodered.
20. To run console commands for a container you need to run:

docker exec -it \&lt;containername\&gt; bash

21. To configure for my application I need to setup the influxDB first:

docker exec -it influxdb bash

influx

create database home

use home

create user grafana with password &#39;\&lt;passwordhere\&gt;&#39; with all privileges

grant all privileges on home to grafana

22. Next you go to the web address for grafana and login with admin, admin then create a new password.
23. Then you setup a data source for grafana to indicate you&#39;re using an influxdb and put in the username &#39;grafana&#39; and the password you setup. Also database name of &quot;home&quot;
24. Then you can define a dashboard, panels, and queries. These will chart your data however you want. The micro-controllers govern the influx measurement, in my case, &#39;environment&#39; and individual names like Temperature, Humidity, Pressure, etc.
