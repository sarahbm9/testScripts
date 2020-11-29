import paho.mqtt.client as mqtt
import math
import time

def closest(lst, K): 
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))] 

class Navigation:
    def __init__(self):
        self.currentPos = (0,0)
        self.currentMove = (3,0)
        self.goalPos = (10,30)
        self.goalPosPolar = (math.tan(self.goalPos(1)-self.currentPos(1)/(self.goalPos(0)-self.currentPos(0))), math.sqrt((self.goalPos(0)-self.currentPos(0))**2 + (self.goaPos(1)-self.currentPos(1))**2))
        self.angleVec = [-90 -60 -30 0 30 60 90]
        
    def decideMovement(self, distance, angle):
        #THIS WILL DECIDE NEXT MOVE need to update currentPos, and curentMove
        maxD = max(distance)
        maxIndex = distance.index(maxD)
        self.goalPosPolar = (math.tan(self.goalPos(1)-self.currentPos(1)/(self.goalPos(0)-self.currentPos(0))), math.sqrt((self.goalPos(0)-self.currentPos(0))**2 + (self.goaPos(1)-self.currentPos(1))**2))
        angVal = cosest(self.angleVec, self.goalPosPolar(0))
        angValInd = self.angleVec.index(angVal)
        testVec = []
        distVec = []
        testVec.append(angValInd)
        if angVal == 0:
            testVec.append(angValInd + 1)
        elif angVec == len(self.angleVec):
            testVec.append(angValInd-1)
        else:
            testVec.append(angValInd-1)
            testVec.append(angValInd + 1)

        for ind in testVec:
            distVec.append(distance[ind])
        
        minVal = min(distVec)
        maxVal = max(distVac)
        if minVal > 0.8*maxVal:
            self.currentMove = (angle[maxIndex], distance[maxIndex])
        elif distance[angValInd] > 0.9*maxVal:
            self.currentMove = (angle[angValInd], distance[angValInd])
        else:
            maxTestInd = distance.index(maxVal)
            self.currentMove = (angle[maxTestInd], distance[maxTestInd])
        self.currentPos = (self.currentMove(1)*math.cos(math.pi/180*self.currentMove(0)),self.currentMove(1)*math.sin(math.pi/180*self.currentMove(0)))


    


class MQTThandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.nav = Navigation()

        self.client.username_pw_set("dhnngvfj", "zhM1Ds0tjbnC")
        self.client.connect("m16.cloudmqtt.com", port=18367)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.loop_start()
        self.client.subscribe("cc32xx/sMsg")

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
        angle_hold = [angle_val["ang0"]*np.pi/180, angle_val["ang30"]*np.pi/180, angle_val["ang60"]*np.pi/180, angle_val["ang90"]*np.pi/180, angle_val["ang120"]*np.pi/180, angle_val["ang150"]*np.pi/180, angle_val["ang1800"]*np.pi/180 ]
        if sum(isGoal_hold) == 0:
            self.nav.decideMovement(distance_hold, angle_hold)
            self.client.publish("cc32xx/navigation", '{"state": no goal found, "distance": '+str(self.nav.curentMove(0))', "angle":'+str(self.nav.curentMove(1))+'}')
        else:
            index = isGoal_hold.index(1)
            self.nav.currentMove = (angle_hold[index], distance_hold[index])
            self.client.publish("cc32xx/navigation", '{"state": goal found, "distance": '+str(self.nav.curentMove(0))', "angle":'+str(self.nav.curentMove(1))+'}')

if __name__ == "__main__":
    mt = MQTThandler()
