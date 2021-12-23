"""""
===============================================================================
Industrial Internet of Things (IIoT) Retrofit - PLC Application
-----------------------------------------------
This application is to be run on an IoT device on the manufacturing floor.

It will connect to EtherNet/IP devices (PLCs) and extract process information
from them.

This information is then sent to a Cloud based application via MQTT in a 
JSON format.

Updated setpoints are then returned to this application which notifies the 
Operator through the turning on of the SenseHat LEDs. The updated setpoint 
can then be sent to the PLC via a POST request.

The operator can also read the current setpoint by performing a GET request.

===============================================================================
"""

from pycomm3 import LogixDriver
from urllib.parse import urlparse
from dotenv import dotenv_values
from flask import Flask, request, render_template
from flask_cors import CORS
import paho.mqtt.client as mqtt
import time
import datetime
import json
from sense_hat import SenseHat
from threading import Thread

#Initialize SenseHat
sense = SenseHat()

#Set program start time and enviroment variables file
start_time = time.time()
config = dotenv_values("assignment/.env")
new_setpoint_flag = False
new_setpoint_payload = ""

#create Flask app instance and apply CORS
app = Flask(__name__)
CORS(app)

#Routes for GET & POST requests
#Read setpoint value from PLC and return
@app.route('/iiot',methods=['GET'])
def current_setpoint():
    setpoint = read_single('MQTT_Setpoint')
    return str(setpoint)

#Write new setpoint value to PLC and clear SenseHat LEDs
@app.route('/iiot',methods=['POST'])
def ack_setpoint():  
    global new_setpoint_payload
    write_single(new_setpoint_payload)
    sense.clear([0,0,0])
    return "New setpoint applied: " + str(new_setpoint_payload)

#Run HTTP API on port 5000
def runApp():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

#Setup PLC communications
#Function to read tag value from PLC
def read_single(tag):
    with LogixDriver('10.155.3.2/1') as plc:
        return plc.read(tag)

#Function to write value to PLC MQTT Setpoint tag
def write_single(value):
    with LogixDriver('10.155.3.2/1') as plc:
        print("Updated PLC setpoint: " + value)
        return plc.write('MQTT_Setpoint', float(value))

# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connection Result: " + str(rc))

def on_publish(client, obj, mid):
    print("Message ID: " + str(mid))

def on_message(client, obj, msg):
    global new_setpoint_flag
    global new_setpoint_payload
    msg.payload = msg.payload.decode("utf-8")
    if msg.topic == "pmarnane/home/setpoint":
        print("New setpoint available")
        new_setpoint_payload = msg.payload
        new_setpoint_flag = True

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed,  QOS granted: "+ str(granted_qos))

#Function to notify operator of new setpoint
def indicatorOn(value):
    #sense.show_message(text_string="New Setpoint Available", text_colour=(255,0,0))
    sense.clear(255,0,0)

#MQTT Client setup
mqttc = mqtt.Client()
mqttc.tls_set('assignment/ca.crt')

# Assign event callback
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_message = on_message
mqttc.on_subscribe = on_subscribe

# parse mqtt url for connection details
url_str = config["mqtt_url"]
print(url_str)
url = urlparse(url_str)
base_topic = url.path[1:]

#Connect to Mosquitto MQTT Broker
mqttc.username_pw_set(config["username"], config["password"])
mqttc.connect(url.hostname, url.port)
mqttc.loop_start()
mqttc.subscribe(base_topic+"/setpoint")


def main():
    while True:
        global start_time
        global new_setpoint_flag
        global new_setpoint_payload
        
        updated_time = time.time()

        #Use time values to trigger publishing data rather than sleeping thread
        if (updated_time - start_time) >= 5:
            #Read MQTT tag values in PLC and add timestmap
            x = read_single('MQTT')
            plcValue = x[1]
            plcValue['tStamp'] = datetime.datetime.utcnow()
            
            #Convert PLC values to JSON and publish on IIoT topic
            temp_json=json.dumps(plcValue, default=str)
            mqttc.publish(base_topic+"/iiot", temp_json, 2)
            start_time = time.time()
        #New setpoint has arived from Cloud app
        #Set up Operator indicator
        if new_setpoint_flag:
            indicatorOn(new_setpoint_payload)
            new_setpoint_flag = False

if __name__ == "__main__":
    #Seperate thread for HTTP API app ad app main entry
    Thread(target = runApp).start()
    Thread(target = main()).start()