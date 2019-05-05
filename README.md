# Bike Rack

This is project that makes use the state machine framework for python [STMPY](https://pypi.org/project/stmpy/). The project has not been tested with the latest version of STMPY (so the version prior to the April 9. version), so users be aware of problems with the newer release. The project also makes use of the [MQTT application layer protocol](https://pypi.org/project/paho-mqtt/) and its implementation in Pyton. 

The project in its current state is a prototype of a system of reservable smart bike locks. You can reserve a lock at a bike rack of your choice, ride your bike to rack and lock your bike there without any hassle. 

## Install and Run
The project runs on a Raspberry PI model 3B. To run the project follow these steps: 
* Install Python 3.7 on your raspierry Pi
* Install the libraries needed to run NXPPY. Follow [these steps](https://github.com/svvitale/nxppy)
* Remember to enable GPIO on your Raspberry Pi. 
* You need a MQTT-broker for the rack to connect to. We recommend [mosquitto](https://mosquitto.org/)
* We highly recommend you run this application in a Python virtual environment
* `pip install -r requirement.txt`

This project runs several python modules in paralell processes on the PI. In three different terminals run: 
* `python server_listener.py`
* `python nfc_component.py`
* `python bike_rack.py`

To test the system you can either use the entire system by also running the [phone app](https://github.com/ttm4115-group11/phone-app/) and [web server](https://github.com/ttm4115-group11/webserver), or you can send commands directly to the system by using either the `mosquitto_pub`-command that you get with mosquitto or a graphical MQTT interface such as [MQTT.fx](https://mqttfx.jensd.de/).
