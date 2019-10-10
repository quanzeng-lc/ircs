#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
import random


class UltraSoundModule(object):
    def __init__(self, parent, context):
	self.context = context
        self.parent = parent
	self.flag = True

	self.distance = 10

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.Trig = 2
        self.Echo = 3
        GPIO.setup(self.Trig, GPIO.OUT, initial=GPIO.LOW)
	GPIO.setup(self.Echo, GPIO.IN)
	#self.moveTask = threading.Thread(None, self.read)
       	#self.moveTask.start()
    
    def read_current_distance(self):
	GPIO.output(self.Trig, True)
        time.sleep(0.00001)
        GPIO.output(self.Trig, False)
        while GPIO.input(self.Echo) == 0:
              pass
        start = time.time()
        while GPIO.input(self.Echo) == 1:
              pass
        end = time.time()
        return round(((end-start)*340*100/2),2)
				
    def read(self):
	cpt = 0
        while self.flag:
					
		GPIO.output(self.Trig, True)
		time.sleep(0.00001)
		GPIO.output(self.Trig, False)
		while GPIO.input(self.Echo) == 0:
			pass
		start = time.time()
		while GPIO.input(self.Echo) == 1:
			pass
		end = time.time()
			
		self.distance = round(((end-start)*340*100/2),2)
		print self.distance	
		
		time.sleep(0.2)
		
		#self.parent.set_global_guidewire_distance(self.distance)
		cpt += 1


#x = UltraSoundModule(0,0)
#x.read()
	
