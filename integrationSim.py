import paho.mqtt.client as mqtt
import time

client = mqtt.Client()

client.username_pw_set("dhnngvfj", "zhM1Ds0tjbnC")
client.connect("m16.cloudmqtt.com", port=18367)

print("sending...")


client.publish("cc32xx/ARMStatus", '{"Block": "droppedOff"}')

print("sent arm done")
time.sleep(1)

client.publish("cc32xx/MRStatus", '{"status": "FOLLOWING_ROVER"}')

print("sent mini rover done")

client.disconnect()
