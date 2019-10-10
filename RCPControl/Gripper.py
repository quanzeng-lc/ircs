#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time


class Gripper(object):
	def __init__(self, io):
		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		self.flag = True	
		self.count = 0
		self.io = io
		GPIO.setup(self.io, GPIO.OUT, initial=GPIO.LOW)

	def gripper_chuck_fasten(self):
		GPIO.output(self.io, True)
	
	def gripper_chuck_loosen(self):
		GPIO.output(self.io, False)	
