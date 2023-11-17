import paho.mqtt.client as paho
import sys
from time import sleep
import json

d = 0
print("LampShowerSoftware v1.0")
ip = input("Please enter the broker's IP address:\n")
topicBase = input("Please enter topic base name:\n")
lamp = input("Please enter the port that the lamp is connected to (1-8):\n")
while not lamp in "12345678":
    lamp = input("Please input an integer between 1 and 8")
sensor = input("Please enter the port that the sensor is connected to (1-8):\n")
while not sensor in "12345678":
    sensor = input("Please input an integer between 1 and 8")


def onmsg(client, userdata, msg):
    #print(msg.topic + ": " + msg.payload.decode())
    global d
    if(msg.topic == topicBase+"/port/"+sensor+"/pdi"):
        payload_json = json.loads(msg.payload.decode())
        process_meter = payload_json['P_Process_Meter']
        dist = process_meter['Measurement_value__Distance']
        d = dist
        print("Measured distance:", dist)
        return

def onconnect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topicBase+"/port/"+sensor+"/pdi")
    client.subscribe("test")

client = paho.Client()
client.on_message = onmsg
client.on_connect = onconnect

if client.connect(ip, 1883, 60) != 0:
    print("can't connect :(")
    sys.exit(-1)

#client.subscribe("MqttTopicBase/port/5/pdi")
#client.subscribe("test")

client.publish(topicBase+"/port/"+lamp+"/pdo/wr", "Controlling with Python")
client.publish("test", "Controlling with Python")

def sigmoid(x):
    if x < 50:
        return 0
    if x > 650:
        return 255
    return int((x-50)/600*255)

try:
    i = 0
    while True:
        #level = int(input("Enter how many % of the lamp you want to light\n"))
        sleep(.05)
        client.loop()
        i += 10
        if(i >= 100):
            i = 0
        level = i
        client.publish(topicBase+"/port/"+lamp+"/pdo/wr", "{\"port\": "+lamp",\"valid\": 1,\"raw\":[17, 2, 0, 2, 0, 0, "+str(sigmoid(d))+", 0]}", 0)

except Exception as e:
    print("You've pressed ^C; disconnectiong")
    print(e)

client.disconnect()
