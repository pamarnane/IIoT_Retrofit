# Industrial IoT – Retrofit for Industry 4.0
#### Student Name: *Patrick Marnane*   Student ID: *03208003*

The Internet of Things (IoT) is just not limited to Home Automation, Sensors etc. There is also Industrial IoT (IIoT) which looks to connect the equipment and devices on the manufacturing floor to the Cloud to enable smarter business decisions.
One of the barriers of this move is the amount of legacy equipment that exists that does not have the capability to connect to the Cloud and the cost of the replacement, especially in validated environments (Pharma, Med Device, etc)
This project will enable existing manufacturing controls equipment to send information to the cloud and receive updated setpoints for processes.


## Tools, Technologies and Equipment

The overall concept for this is to have a single board computer (Raspberry Pi) to connect to a Programmable Logic Controller (PLC) which communicates over EtherNet/IP protocol.
This Raspberry Pi will run a Python application that extract process information from the PLC over EtherNet/IP and send an MQTT message to a broker, possibly at an interval of every 5 seconds.
A Java application will be listening for this information to be sent on the topic and will write this data to an SQL DB. After a defined period of time (1 hour), the application will analyse the received data from the previous hour and generate updated process setpoints.
These updated setpoints will can then be sent back to an Operator on the manufacturing floor via a mobile app or emial (Blynk.io, mailgun etc) who will approve these values.
The Java application will then send an MQTT message containing the updated setpoints back to the Raspbery via MQTT who will in turn write them to the PLC.


## Project Repository

https://github.com/pamarnane/IIoT_Retrofit


