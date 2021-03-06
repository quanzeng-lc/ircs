#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
import random


class EmergencySwitch(object):
    def __init__(self):
        self.switch = 5
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.switch, GPIO.IN)

    def read_current_state(self):
        sw = GPIO.input(self.switch)
        return sw

"""
for i in range(100):
    switch = EmergencySwitch()
    print switch.read_current_state()
    time.sleep(1)
"""
