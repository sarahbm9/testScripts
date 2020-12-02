import paho.mqtt.client as mqtt
import math
import time
import json


#I'm just storing the current state in nav.curState as a raw int to keep things simple

class Navigation:
    def __init__(self):
        self.curState = 0   #states: SEARCH_1 = 0, SEARCH_2 = 1, MOVE = 2
        self.prevState = 0
        self.roverReady = 1 #tracks whether or not the rover is ready to received a new nav instruction
        self.curAngle = 0   #current angle that will be sent to the rover in the next message
        self.prevAngle = 0  #previous angle that was received from movement.py
        self.curDist = 0    #current distance that will be sent to the rover in the next message
        self.prevDist = 0   #previous distance that was received from movement.py

    def no_goal_found(self, input_vals):         #state transitions for when no goal has been found
        self.goalFound = 0
        self.roverReady = 0
        if self.curState == 0:                 #if curstate is SEARCH_1
            if self.prevState == 1:            #if rover just turned back because goal still not found
                self.curAngle = self.prevAngle
                self.curDist = self.prevDist
                self.prevState = self.curState
                self.curState = 2
            else:
                self.prevAngle = input_vals["angle"]  #store suggested angle and distance for potential use later
                self.curAngle = 180
                self.prevDist = input_vals["distance"]
                self.curDist = 0
                self.prevState = self.curState
                self.curState = 1               #next state will be SEARCH_2

        elif self.curState == 1:  #WHAT BEHAVIOR DO WE WANT IN THIS CASE?
            self.prevState = self.curState
            self.curState = 0
            self.curAngle = -180
            self.curDist = 0

        elif self.curState == 2:                  #if curstate is MOVE
            self.curState = 0                     #next state will be SEARCH_1

    def goal_found(self, input_vals):            #There should only be one state transition when the goal is found
            self.goalFound = 1
            self.roverReady = 0
            self.prevAngle = self.curAngle
            self.curAngle = input_vals["angle"]
            self.prevDist = self.curDist
            self.curDist = input_vals["distance"]
            self.prevState = self.curState
            self.curState = 2
            if self.curDist < 200:
                self.curState = 10

class MQTThandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.nav = Navigation()

        self.client.username_pw_set("dhnngvfj", "zhM1Ds0tjbnC")
        self.client.connect("m16.cloudmqtt.com", port=18367)
        self.client.on_connect = self.on_connect
        #self.client.on_message = self.on_message
        self.client.message_callback_add("cc32xx/mapOut", self.on_map_message)
        self.client.message_callback_add("cc32xx/RoverReady", self.on_rover_message)

        self.client.loop_start()
        self.client.subscribe("cc32xx/#")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected to broker")

        else:
            print("connection failed")

    def on_map_message(self,client, userdata, message):
        print("map message recieved...")
        input_vals = json.loads(message.payload.decode('utf-8'))
        #print(input_vals)
        if self.nav.roverReady == 1:
            if input_vals["state"] == "no goal found":
                self.nav.no_goal_found(input_vals)
            else:
                self.nav.goal_found(input_vals)
            if self.nav.curState != 10:
                self.client.publish("cc32xx/navigation", '{"distance": '+str(self.nav.curDist)+', "angle" :'+str(self.nav.curAngle)+'}')
            self.client.publish("TR/navScript", '{"curState": '+str(self.nav.curState)+', "prevState": '+str(self.nav.prevState)+', "RoverReady": '+str(self.nav.roverReady)+', "curAngle": '+str(self.nav.curAngle)+', "prevAngle": '+str(self.nav.prevAngle)+', "curDist": '+str(self.nav.curDist)+', "prevDist": '+str(self.nav.prevDist)+'}')

    def on_rover_message(self, client, userdata, message):
        print("rover ready message received...")
        self.nav.roverReady = 1
        if self.nav.curState == 2:
            self.nav.prevState = self.nav.curState
            self.nav.curState = 0
        self.client.publish("TR/navScript", '{"curState": '+str(self.nav.curState)+', "prevState": '+str(self.nav.prevState)+', "RoverReady": '+str(self.nav.roverReady)+', "curAngle": '+str(self.nav.curAngle)+', "prevAngle": '+str(self.nav.prevAngle)+', "curDist": '+str(self.nav.curDist)+', "prevDist": '+str(self.nav.prevDist)+'}')

if __name__ == "__main__":
    mt = MQTThandler()
    while 1:
        time.sleep(0.1)
