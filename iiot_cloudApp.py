"""""
===============================================================================
Industrial Internet of Things (IIoT) Retrofit - Cloud Application
-----------------------------------------------
This application is to be run on an server that must be able to communicate
to the MQTT Broker.

It will receive process information from the accompanying application via MQTT
and write the values to a MongoDB instance.

After a set period of time (2 mins in this example), the application will pull
the data for that time period and send an updated setpoint to the PLC application.

===============================================================================
"""

from datetime import datetime, timedelta
from dotenv import dotenv_values
from urllib.parse import urlparse
from pymongo import MongoClient
import paho.mqtt.client as mqtt
import json

#Load configuration values from .env file
config = dotenv_values("iiot/.env")

#Create MongoClient connection
client = MongoClient(config["mongodb_uri"],
                     tls=True,
                     tlsCertificateKeyFile='/root/iiot/X509-cert-3358569558120399419.pem')
db = client.IIoT

#Function to write payload to MongoDB
def mongoWrite(payload):
    post = json.loads(payload)
    #Convert timestamp from String to DateTime
    post['tStamp'] = datetime.strptime(post['tStamp'], "%Y-%m-%d %H:%M:%S.%f")
    db.LineXX.insert_one(post).inserted_id

#Set up MQTT communications
mqttc = mqtt.Client()
mqttc.tls_set('iiot/ca.crt')

# Define MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    print("Connection Result: " + str(rc))

def on_message(client, obj, msg):
    msg.payload = msg.payload.decode("utf-8")
    if msg.topic == "pmarnane/home/iiot":
        print(msg.payload)
        mongoWrite(msg.payload)

def on_subscribe(client, obj, mid, granted_qos):
    print("Subscribed,  QOS granted: "+ str(granted_qos))

def publishMessage(payload):
    mqttc.publish


def main():
    sp_minute = 0
    
    # Assign MQTT event callbacks
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_subscribe = on_subscribe

    #Parse MQTT url for connection details
    url_str = config["mqtt_url"]
    url = urlparse(url_str)
    base_topic = url.path[1:]

    # Connect to local Mosquitto MQTT Broker
    mqttc.username_pw_set(config["username"], config["password"])
    mqttc.connect(url.hostname, url.port)

    # Start subscribe to IIoT topic
    mqttc.subscribe(base_topic+"/iiot")
    rc = mqttc.loop_start()

    # Continue the network loop, exit when an error occurs
    while True:
        #Check if 2 minutes has elapsed since last setpoint update
        if (datetime.now().minute % 2) == 0 and sp_minute != datetime.now().minute:
            d = datetime.now() - timedelta(minutes=2)  
            add_temp = 0
            count = 0
            #For loop to get all documents uploaded in lat 2 minutes
            for post in db.LineXX.find({"tStamp": {"$gte": d}}):
                add_temp += post["temp"]
                count += 1
            #Verify that process values have been recorded for last time period
            #Calculate average and publish to 'setpoint topic
            if count != 0:
                average = add_temp/count
                print("Updated setpoint: " + str(average))
                mqttc.publish(base_topic+'/setpoint', average, 2)
            sp_minute = datetime.now().minute
            
    print("rc: " + str(rc))

if __name__ == "__main__":
    main()