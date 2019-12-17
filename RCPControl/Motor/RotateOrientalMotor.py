#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
from RCPContext.RCPContext import RCPContext


class RotateOrientalMotor(object):
    def __init__(self):
        
        self.orientalMotorPushLock = threading.Lock()
        self.orientalMotorPullLock = threading.Lock()
#       self.orientalMotorPositionPushLock = threading.Lock()
#	self.orientalMotorPositionPullLock = threading.Lock()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.pushIO = 19
        self.pullIO = 26
        GPIO.setup(self.pushIO, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.pullIO, GPIO.OUT, initial=GPIO.HIGH)
        self.flag = True
        self.pos_flag = True
        self.expectedSpeedFlag = 0
        # count the pulse to calculate the rotating speed deg/s
        self.count = 0
        self.context = None

        #parametertype id
        self.hapticFeedbackID = 0

	#mode choose
        self.mode = True
        self.max_interval = 0

        #parameter resolution: degree/pulse
        self.deg_pulse = 0.36
        # grae ratio
        self.gear_ratio = 2.0

        #velocity mode degree/s
        self.expectedSpeed = 0
        self.vel_mode_interval = self.max_interval

        # actual speed degree/s
        self.actualVelocity = 0

        #position mode
        self.pos_motor_flag = 1
        self.rotate_angle = 0
        self.pos_expectedSpeed = 60.0
	
        self.pos_count = 0
#	self.all_sleep_time = 0
        
        self.mv_enable = True

        if self.mode:
            self.moveTask = threading.Thread(None, self.continuous_move)
            self.moveTask.start()
#	else:
#	    self.moveTask = threading.Thread(None, self.continuous_move_position)
#            self.moveTask.start()

        # monitoring the motor status
        self.statusParameterTask = threading.Thread(None, self.statusMonitoring)
        #self.statusParameterTask.start()


    def open_device(self):
        self.flag = True

    def close_device(self):
        self.flag = False

    def close_position_device(self):
        self.pos_flag = False

    def set_expectedSpeed(self, speed):
        if speed > 0:
            self.expectedSpeedFlag = 1
            self.vel_mode_interval = self.deg_pulse/(self.gear_ratio*speed*2.0)
        elif speed < 0:
            self.expectedSpeedFlag = 2
            self.vel_mode_interval = abs(self.deg_pulse/(self.gear_ratio*speed*2.0))
        elif speed == 0:
            self.expectedSpeedFlag = 0
        self.expectedSpeed = abs(speed)
   
    def standby(self):
        if self.mv_enable == False:
            return
        self.mv_enable = False
    
    def enable(self):
        if self.mv_enable == True:
            return
        self.mv_enable = True

    def continuous_move(self):
        while self.flag:            
            if self.mv_enable:
                if self.expectedSpeedFlag == 0:
                    time.sleep(0.1)

                if self.expectedSpeedFlag == 1:
                    self.push()
            
                if self.expectedSpeedFlag == 2:
                    self.pull()
            else:
                time.sleep(0.5)

	    
    def rtz(self):
        GPIO.output(self.pushIO, True)
        GPIO.output(self.pullIO, True)
    
    def push(self):
        self.orientalMotorPushLock.acquire()
        interval = self.max_interval
        if self.expectedSpeed == 0:
            return 
        else:
            interval = self.vel_mode_interval
            #print "interval:", interval
        self.orientalMotorPushLock.release()
        GPIO.output(self.pushIO, False)              
        time.sleep(interval)                
        GPIO.output(self.pushIO, True)
        time.sleep(interval)
        self.count += 1

    def pull(self):
        self.orientalMotorPushLock.acquire()
        interval = self.max_interval
        if self.expectedSpeed == 0:
            return 
        else:
            interval = self.vel_mode_interval
        self.orientalMotorPushLock.release()
        GPIO.output(self.pullIO, False)
        time.sleep(interval)
        GPIO.output(self.pullIO, True)
        time.sleep(interval) 
        self.count += 1


    #Position Mode    #############################1
    def set_position(self, angle):
        self.rotate_angle = angle
#	print self.rotate_angle
#	self.pos_count+= self.rotate_angle

    def set_pos_expectedSpeed(self, speed):
        self.pos_expectedSpeed = speed
#	print self.pos_expectedSpeed
        
    def continuous_move_position(self):
        while self.pos_flag:                     
            if self.rotate_angle > 0:                   
                self.rotate_angle_push()
                time.sleep(self.get_position_sleep_time())
#		self.pos_flag = False
            elif self.rotate_angle < 0:
                self.rotate_angle_pull()
                time.sleep(self.get_position_sleep_time())
            elif self.rotate_angle == 0:
                time.sleep(0.001)
#		self.pos_flag = False
    

    def stop(self):
        self.set_position(0)
        self.set_expectedSpeed(0)
        self.set_pos_expectedSpeed(0)
        time.sleep(0.01)
        self.pos_count = 0
    
    def position_push(self):
#	self.orientalMotorPositionPushLock.acquire()
#	print self.pos_motor_flag
        interval = 0
        if self.rotate_angle == 0 or self.pos_expectedSpeed == 0:
            pulse_number = 0
            interval = 0
        else:
            pulse_number = int(self.gear_ratio*self.rotate_angle/self.deg_pulse)
            interval = self.deg_pulse/(self.gear_ratio*self.pos_expectedSpeed*2.0)
#	print pulse_number
#	print interval
        for i in range(0, pulse_number): 
            GPIO.output(self.pushIO, False)              
            time.sleep(interval)                
            GPIO.output(self.pushIO, True)
            time.sleep(interval)
#	self.orientalMotorPositionPushLock.release()

            
    def position_pull(self):
        self.orientalMotorPositionPullLock.acquire()
        interval = self.max_interval
        if self.rotate_angle == 0 or self.pos_expectedSpeed == 0:
            pulse_number = 0
            interval = self.max_interval
        else:
            pulse_number = int(self.gear_ratio*self.rotate_angle/self.deg_pulse)
            interval = self.deg_pulse/(self.gear_ratio*self.pos_expectedSpeed*2.0)
        self.orientalMotorPositionPullLock.release()
#	print pulse_number
        for i in range(0, pulse_number):
            GPIO.output(self.pullIO, False)              
            time.sleep(interval)             
            GPIO.output(self.pullIO, True)
            time.sleep(interval)

    def setContext(self, context):
        self.context = context

    def setParameterTypeID(self, ID):
        self.hapticFeedbackID = ID

    # monitoring the motor status
    def statusMonitoring(self):
        # To do..........
        while True:



            if self.context is not None:
                self.context.setGlobalParameter(self.hapticFeedbackID, self.expectedSpeed)
            time.sleep(0.03)

"""
motor1 = RotateOrientalMotor()
motor1.enable()
#motor1.set_position(5)
#motor1.set_pos_expectedSpeed(5)
start = time.time()
#motor1.position_push()
motor1.set_expectedSpeed(10)
time.sleep(2)
motor1.stop()
print time.time()-start
"""
