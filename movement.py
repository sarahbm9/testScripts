import paho.mqtt.client as mqtt
import json
import numpy as np
import math
import time
import matplotlib.pyplot as plt

def closest(lst, K): 
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))] 

def get_index_positions(list_of_elems, element):
    ''' Returns the indexes of all occurrences of give element in
    the list- listOfElements '''
    index_pos_list = []
    index_pos = 0
    while True:
        try:
            # Search for item in list from indexPos to the end of list
            index_pos = list_of_elems.index(element, index_pos)
            # Add the index position in list
            index_pos_list.append(index_pos)
            index_pos += 1
        except ValueError as e:
            break
    return index_pos_list


class Navigation:
    def __init__(self):
        self.flag = 1
        self.RoverReady = 1
        self.currentMove = (0,0)
        self.prevDist = []
        self.prevAngle = []
        self.prevGoal = []
        self.goalPosPolar = (30, 0.5) #angle, distance
        self.angleVec = [-90, -60, -30, 0, 30, 60, 90]
        
    def decideMovement(self, distance, angle, distancePrev, anglePrev):
        #THIS WILL DECIDE NEXT MOVE need to update currentPos, and curentMove
        maxD = max(distance)
        maxIndex = distance.index(maxD)
        angVal = closest(self.angleVec, self.goalPosPolar[0])
        angValInd = self.angleVec.index(angVal)
        print(distance[angValInd])  
        print(distancePrev[angValInd])  
        if distance[angValInd] < 500 or distancePrev[angValInd] < 500:
            if angValInd == 0:
                self.currentMove = (min(angle[angValInd +1], anglePrev[angValInd + 1]), min(distance[angValInd +1], distancePrev[angValInd + 1]))
            elif angValInd == len(self.angleVec):
                self.currentMove = (min(angle[angValInd -1], anglePrev[angValInd - 1]), min(distance[angValInd -1], distancePrev[angValInd - 1]))
            else:
                self.currentMove = (min(min(angle[angValInd -1], anglePrev[angValInd - 1]),min(angle[angValInd +1], anglePrev[angValInd + 1])), min(min(distance[angValInd -1], distancePrev[angValInd - 1]),min(distance[angValInd +1], distancePrev[angValInd + 1])))

        else:
            print("HIIII")
            self.currentMove = (self.angleVec[angValInd], 500)

        '''testVec = []
        distVec = []
        testVec.append(angValInd)
        if angVal == 0:
            testVec.append(angValInd + 1)
        elif angVal == len(self.angleVec):
            testVec.append(angValInd-1)
        else:
            testVec.append(angValInd-1)
            testVec.append(angValInd + 1)

        for ind in testVec:
            distVec.append(distance[ind])
        
        minVal = min(distVec)
        maxVal = max(distVec)
        if minVal > 0.8*maxVal:
            self.currentMove = (min(angle[maxIndex], anglePrev[maxIndex]), 0.7*min(distance[maxIndex], distancePrev[maxIndex]))
        elif distance[angValInd] > 0.9*maxVal:
            self.currentMove = (min(angle[angValInd], anglePrev[angValInd]), 0.7*min(distance[angValInd], distancePrev[angValInd]))
        else:
            maxTestInd = distance.index(maxVal)
            self.currentMove = (min(angle[maxTestInd], anglePrev[maxTestInd]), 0.7*min(distance[maxTestInd], distancePrev[maxTestInd]))
'''

    


class MQTThandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.nav = Navigation()

        self.client.username_pw_set("dhnngvfj", "zhM1Ds0tjbnC")
        self.client.connect("m16.cloudmqtt.com", port=18367)
        self.client.on_connect = self.on_connect
        #self.client.on_message = self.on_message
        self.client.message_callback_add("cc32xx/sMsg", self.on_message)
        self.client.message_callback_add("cc32xx/RoverReady", self.on_rover_message)
        self.client.message_callback_add("cc32xx/RoverMoving", self.on_move_message)

        self.client.loop_start()
        self.client.subscribe("cc32xx/#")
    def on_rover_message(self, client, userdata,message):
        self.nav.roverReady = 1
    def on_move_message(self, client, userdata, message):
        self.nav.roverReady = 0
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected to broker")

        else:
            print("connection failed")

    def on_message(self,client, userdata, message): 
        print("message recieved: ")
        angle_val = json.loads(message.payload.decode('utf-8'))
        #print(angle_val)
        angle_hold = [0.0,np.pi/6,np.pi/3,np.pi/2,2*np.pi/3,5*np.pi/6,np.pi]
        distance_hold = [angle_val["d0"], angle_val["d30"], angle_val["d60"], angle_val["d90"], angle_val["d120"], angle_val["d150"], angle_val["d180"]]
        isGoal_hold = [angle_val["isG0"], angle_val["isG30"], angle_val["isG60"], angle_val["isG90"], angle_val["isG120"], angle_val["isG150"], angle_val["isG180"]]
        angle_hold = [angle_val["ang0"], angle_val["ang30"], angle_val["ang60"], angle_val["ang90"], angle_val["ang120"], angle_val["ang150"], angle_val["ang1800"]]
        angle_hold2 = []
        for ang in angle_hold:
            if ang < 0:
                ang = ang + 360
            angle_hold2.append(ang)
        angle_hold = angle_hold2
        if not self.nav.flag and self.nav.RoverReady:
            if self.nav.prevDist:
                if sum(isGoal_hold) == 0:
                    self.nav.decideMovement(distance_hold, angle_hold, self.nav.prevDist, self.nav.prevAngle)
                    self.client.publish("cc32xx/mapOut", '{"state": "no goal found", "distance": '+str(self.nav.currentMove[1])+', "angle":'+str(self.nav.currentMove[0])+'}')
                elif sum(isGoal_hold) > 1:
                    indVals = get_index_positions(isGoal_hold, 1)
                    minVal = 4000
                    for ind in indVals:
                        minVal = min(minVal, distance_hold[ind], self.nav.prevDist[ind])
                    #print(angle_hold[indVals[0]])
                    #print(angle_hold[indVals[1]])
                    print(abs(angle_hold[indVals[0]] - angle_hold[indVals[1]]))
                    if abs(angle_hold[indVals[0]] - angle_hold[indVals[1]]) < 15:
                        angle = (angle_hold[indVals[0]] + angle_hold[indVals[1]] + self.nav.prevAngle[indVals[0]]+ self.nav.prevAngle[indVals[1]])/4
                        distance = (distance_hold[indVals[0]] + distance_hold[indVals[1]] + self.nav.prevDist[indVals[0]] + self.nav.prevDist[indVals[1]])/4
                        self.nav.currentMove = (angle, 0.7*distance)
                        self.client.publish("cc32xx/mapOut", '{"state": "goal found", "distance": '+str(self.nav.currentMove[1])+', "angle":'+str(self.nav.currentMove[0])+'}')
                    elif minVal < 200:
                        self.nav.currentMove = (0, minVal)
                        self.client.publish("cc32xx/mapOut", '{"state": "goal found", "distance": '+str(self.nav.currentMove[1])+', "angle":'+str(self.nav.currentMove[0])+'}')
                    else:
                        self.nav.decideMovement(distance_hold, angle_hold, self.nav.prevDist, self.nav.prevAngle)
                        self.client.publish("cc32xx/mapOut", '{"state": "multiple goals", "distance": '+str(self.nav.currentMove[1])+', "angle":'+str(self.nav.currentMove[0])+'}')
                else:
                    index = isGoal_hold.index(1)
                    angle = min(angle_hold[index], self.nav.prevAngle[index])
                    distance = min(distance_hold[index] , self.nav.prevDist[index])
                    self.nav.currentMove = (angle, 0.7*distance)
                    self.client.publish("cc32xx/mapOut", '{"state": "goal found", "distance": '+str(self.nav.currentMove[1])+', "angle":'+str(self.nav.currentMove[0])+'}')
                self.nav.prevDist = []
                self.nav.prevAngle = []
                self.nav.prevGoal = []
            else:
                self.nav.prevDist = distance_hold
                self.nav.prevAngle = angle_hold
                self.nav.prevGoal = isGoal_hold

        else:
            self.nav.flag = 0

if __name__ == "__main__":
    mt = MQTThandler()
    while 1:
        time.sleep(0.1)
