#{"d0": 3987, "isG0": 0,"ang0": 300.38, "d30": 3904, "isG30": 0,"ang30": 320.38,"d60": 3955, "isG60": 0,"ang60": 340.38,"d90": 3965, "isG90": 0,"ang90": 0.38,"d120": 3973, "isG120": 0,"ang120": 20.38,"d150": 3969, "isG150": 0,"ang150": 40.38,"d180": 3970, "isG180": 0,"ang1800": 60.38 }
import paho.mqtt.client as mqtt
import time

client = mqtt.Client()

client.username_pw_set("dhnngvfj", "zhM1Ds0tjbnC")
client.connect("m16.cloudmqtt.com", port=18367)

print("sending...")


client.publish("cc32xx/sMsg", '{"d0": 1239, "isG0": 0,"ang0": 300.38, "d30": 500, "isG30": 0,"ang30": 320.38,"d60": 500, "isG60": 0,"ang60": 340.38,"d90": 1235, "isG90": 0,"ang90": 0.38,"d120": 2000, "isG120": 0,"ang120": 20.38,"d150": 1000, "isG150": 0,"ang150": 40.38,"d180": 2300, "isG180": 0,"ang1800": 60.38 }')
print("sent sensor map")

client.disconnect()
