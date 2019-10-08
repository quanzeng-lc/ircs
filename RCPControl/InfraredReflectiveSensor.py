#!/usr/bin/env python
# encoding: utf-8

#import RPi.GPIO as GPIO
import time
import threading
import random
from EmergencySwitch import EmergencySwitch


class InfraredReflectiveSensor(object):
    def __init__(self):
        self.doutBack = 2
	self.doutFront = 3
    	self.flag = True

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	GPIO.setup(self.doutBack, GPIO.IN)
	GPIO.setup(self.doutFront, GPIO.IN)

        self.switch = EmergencySwitch()

    def read_current_state(self):
	back = GPIO.input(self.doutBack)
        front = GPIO.input(self.doutFront)
        emSwitch = self.switch.read_current_state() 

        if emSwitch == 1:
            #print 'stop', emSwitch
            return 4
        else:
            #print emSwitch
	    #print "front", front,"back", back
            if back == 0 and front == 1:
                #print 'start move'
                return 1
            if back == 1 and front == 0:
                #print 'start retract'
                return 2
	    if back == 0 and front == 0:
	        #print 'stop'
                return 3
	return 0

    def read(self):
        cpt = 0
        while self.flag:
    	    self.read_current_state()
       	    time.sleep(0.5)

#irs = InfraredReflectiveSensor()
#irs.read()

