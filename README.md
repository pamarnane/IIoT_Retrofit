# Industrial IoT – Retrofit for Industry 4.0
#### Student Name: *Patrick Marnane*   Student ID: *03208003*

## Project Background

The Internet of Things (IoT) is just not limited to Home Automation, Sensors etc. There is also Industrial IoT (IIoT) which looks to connect the equipment and devices on the manufacturing floor to the Cloud to enable smarter business decisions.
One of the barriers of this move is the amount of legacy equipment that exists that does not have the capability to connect to the Cloud and the cost of the replacement, especially in validated environments (Pharma, Med Device, etc)
This project will enable existing manufacturing controls equipment to send information to the cloud and receive updated setpoints for processes.

## Application Functionality

The following is a brief description of how the system operates.

Equipment at the manufacturing floor (i.e. PLC) is connected to an IoT device(Raspberry Pi). This IoT device is running a Python program which will extract process information from the PLC and send it to a Cloud based application via MQTT.

The Cloud based application will store these values in a NoSQL DB(MongoDB) and use the process information to send a suggested process setpoint back to the IoT device that is residing on the manufacturing floor.

The Iot device on the manufacturing floor will notify the operator that an updated setpoint is avaialable by turning on the SenseHat indicator to red. For this project the operator will make an API GET request to the Python application for the updated setpoint value and if they would like to update the setpoint with the value, they can send an API POST request. This API functionality could be added to the existing Line HMI pages.

The Python application will then write the value to the PLC.


## Architecture

![IIot Retrofit Architecture](https://https://github.com/pamarnane/IIoT_Retrofit/img/IIoT_RetroFit_Architecture.png)

The architecture above details the components used for this project and the connections between them.

Devices connecting to the Mosquitto MQTT Broker, Raspberry Pi on the manufacturing floor and the Cloud Debian server, must have the correct Self-Signed CA certificate as well as being authorised with a username and password.

The Debian server running the IIoT Cloud application is authoried to connect to the MongoDB Atlas server via X.509 Certificate.

Due to the site not owning a Static Public IP, a Dynamic DNS hostname was utilised to allow the external applications connect to the devices behing the Firewall/Router. Port forwarding was also implemented so that the MQTT TLS port was not exposed directly on the Public IP.


## Information Flow Diagram

![IIot Retrofit Information Flow](https://https://github.com/pamarnane/IIoT_Retrofit/img/IIoT_RetroFit_InformationFlow.png)

The diagram above represents how information is passed by the various components.


## Project Repository

https://github.com/pamarnane/IIoT_Retrofit

# References

Mosquitto SSL Configuration -MQTT TLS Security: http://www.steves-internet-guide.com/mosquitto-tls/
PyMongo Tutorial: https://pymongo.readthedocs.io/en/stable/tutorial.html
PyComm3 - Ethernet/IP library for communicating with Allen-Bradley PLCs: https://docs.pycomm3.dev/en/latest/
