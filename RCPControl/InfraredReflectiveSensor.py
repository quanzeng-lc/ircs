#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
import random
from RCPControl.EmergencySwitch import EmergencySwitch


class InfraredReflectiveSensor(object):
    def __init__(self):
        self.doutBack = 2
        self.doutFront = 3
        self.flag = True
        self.status = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.doutBack, GPIO.IN)
        GPIO.setup(self.doutFront, GPIO.IN)

        self.switch = EmergencySwitch()
        self.stateTask = threading.Thread(None, self.infraredReflectiveStatus)
        self.stateTask.start()

    def read_current_state(self):
        return self.status

    def infraredReflectiveStatus(self):
        while True:
            back = GPIO.input(self.doutBack)
            front = GPIO.input(self.doutFront)
            emSwitch = self.switch.read_current_state() 

            if emSwitch == 1:
                #print 'stop', emSwitch
                self.status = 4
            else:
                #print emSwitch
                #print "front", front,"back", back
                if back == 0 and front == 1:
                    #print 'start move'
                    self.status = 1
                elif back == 1 and front == 0:
                    #print 'start retract'
                    self.status = 2
                elif back == 0 and front == 0:
                    #print 'stop'
                    self.status = 3
                else:
                    self.status = 0
            time.sleep(0.03)


    def read(self):
        cpt = 0
        while self.flag:
            status = self.read_current_state()
            print(status)
       	    time.sleep(0.05)
"""
irs = InfraredReflectiveSensor()
irs.read()
"""
