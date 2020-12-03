import paho.mqtt.client as mqtt
import time

client = mqtt.Client()

client.username_pw_set("dhnngvfj", "zhM1Ds0tjbnC")
client.connect("m16.cloudmqtt.com", port=18367)

print("sending...")


client.publish("cc32xx/pillsLoaded", '{Pills": "loaded"}')

client.disconnect()
