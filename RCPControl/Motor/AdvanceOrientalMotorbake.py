#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
from AdvanceMotor import AdvanceMotor
from RCPContext.RCPContext import RCPContext

# max velocity 10 mm/s
class AdvanceOrientalMotor(AdvanceMotor):
    def __init__(self):
        
        self.orientalMotorPushLock = threading.Lock()
        self.orientalMotorPullLock = threading.Lock()
#       self.orientalMotorPositionPushLock = threading.Lock()
#	self.orientalMotorPositionPullLock = threading.Lock()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.pushIO = 20
        self.pullIO = 21
        GPIO.setup(self.pushIO, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.pullIO, GPIO.OUT, initial=GPIO.HIGH)
        
        # store the global oarameter
        self.context = None

        # parametertype id
        self.hapticFeedbackID = 0

        # mode choose/default mode: speed mode 
        # True: speed mode  False: position mode
	self.mode = True
        # judge whether the motor is moving 
        self.is_moving = False

        self.is_open = False

        # velocity mode
        self.expectedSpeed = 0
        self.expectedSpeedFlag = 0
        self.count = 0
        # high/low level time interval
        self.velocity_mode_interval = 9999
        # the distance for every circle
        self.dis_circle = 5 #mm
        self.deg_pulse = 0.36 #degree for every pulse
        
        #position mode
        self.pos_motor_flag = 1
	self.pos_flag = True
        self.position = 0
        self.pos_mode_expectedSpeed = 0
        self.pos_mode_expeected_flag = 0
        self.pos_mode_interval = 9999
	
        # actual speed mm/s
        self.actualVelocity = 0

        # count the pulse to calculate the vilocity
	self.pos_count = 0

        # enable
        self.mv_enable = False

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
        if self.is_open == True:
            print "Motor is already open!"
            return 
        self.is_open = True

    def close_device(self):
        if self.is_open == False:
            return
        self.stop()
        
	self.is_open = False

    def standby(self):
        if self.is_moving  == True:
            print "Warning: Motor is moving!"
            return
        if self.mv_enable == False:
            print "Warning: Motor is alraedy not enable!"
            return
        self.mv_enable = False
    
    def enable(self):
        if self.mv_enable == True:
            print "Warning: motor is already enable!"
            return 
        self.stop()
        self.mv_enable = True

    def set_expectedSpeed(self, speed):
        if self.mode is not True:
            return
        if speed > 0:
            self.expectedSpeedFlag = 1
            self.interval = (self.dis_circle*self.deg_pulse)/(speed*360*2.0)
        elif speed < 0:
            self.expectedSpeedFlag = 2
            self.interval = abs((self.dis_circle*self.deg_pulse)/(speed*360*2.0))
        elif speed == 0:
	    self.expectedSpeedFlag = 0
            self.interval = 9999
        self.expectedSpeed = abs(speed)
   
    def start_velocity_mode_move(self):
        if self.mode == True:
            move_task = threading.Thread(self.continuous_move)
            move_task.start()


    def continuous_move(self):
        this.is_moving = True

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
        this.is_moving = False

	    
    def rtz(self):
        GPIO.output(self.pushIO, True)
        GPIO.output(self.pullIO, True)
    
    def push(self):
        self.orientalMotorPushLock.acquire()
	interval = 999999
	if self.expectedSpeed == 0:
	    interval = 999999
            return 
	else:
            interval = self.interval
            #print "interval:", interval
        self.orientalMotorPushLock.release()
        GPIO.output(self.pushIO, False)              
        time.sleep(interval)                
        GPIO.output(self.pushIO, True)
        time.sleep(interval)
        self.count += 1

    def pull(self):
        self.orientalMotorPullLock.acquire()
        interval = 999999
	if self.expectedSpeed == 0:
            interval = 999999
            return 
        else:
            interval = self.interval
        self.orientalMotorPullLock.release()
        GPIO.output(self.pullIO, False)
        time.sleep(interval)
        GPIO.output(self.pullIO, True)
        time.sleep(interval) 
        self.count += 1


    #Position Mode    #############################1
    def set_position(self, position):
        self.position = position
        self.distance_pulse = int((position*360)/(self.dis_circle*self.deg_pulse))
#	print self.position

    def set_pos_mode_expectedSpeed(self, speed):
        if speed > 0:
            self.pos_mode_interval = (self.dis_circle*self.deg_pulse)/(speed*360*2.0)
            self.pos_mod_expected_flag = 1
        elif speed < 0:
            self.pos_mode_interval = abs((self.dis_circle*self.deg_pulse)/(speed*360*2.0))
            self.pos_mod_expected_flag = 2
        elif speed == 0:
            self.pos_mode_interval = 9999
            self.pos_mod_expected_flag = 0
        self.pos_mode_expectedSpeed = abs(speed)
#	print self.pos_mode_expectedSpeed
        
    def continuous_move_position(self):
        while self.pos_flag:                     
            if self.position > 0:                   
                self.position_push()
		time.sleep(self.get_position_sleep_time())
#		self.pos_flag = False
            elif self.position < 0:
                self.position_pull()
		time.sleep(self.get_position_sleep_time())
	    elif self.position == 0:
		time.sleep(0.001)
#		self.pos_flag = False

       
    def stop(self):
        self.flag = False
        self.set_expectedSpeed(0)
	self.set_position(0)
	self.set_pos_mode_expectedSpeed(0)
	time.sleep(0.01)
	self.pos_count = 0

    def position_move(self):
        if self.pos_mod_expected_flag == 1:
            self.position_push()
        elif self.pos_mod_expected_flag == 2:
            self.position_pull()
        else:
            self.stop()
        self.stop()

    def position_push(self):
    #	self.orientalMotorPositionPushLock.acquire()
    #	print self.pos_motor_flag
        interval = 9999
        if self.position == 0 or self.pos_mode_expectedSpeed == 0:
            distance = 0
            interval = 0
        else:
            distance = self.distance_pulse
            interval = self.pos_mode_interval
            print distance
            print interval
        for i in range(0, distance): 
            GPIO.output(self.pushIO, False)              
            time.sleep(interval)                
            GPIO.output(self.pushIO, True)
            time.sleep(interval)
    #	self.orientalMotorPositionPushLock.release()

            
    def position_pull(self):
#	self.orientalMotorPositionPullLock.acquire()
        interval = 9999
	if self.position == 0 or self.pos_mode_expectedSpeed == 0:
            distance = 0
            interval = 0
        else:
            distance = self.distance_pulse
            interval = self.pos_mode_interval
            print distance
            print interval
        for i in range(0, distance):
            GPIO.output(self.pullIO, False)              
            time.sleep(interval)             
            GPIO.output(self.pullIO, True)
            time.sleep(interval)
#	self.orientalMotorPositionPullLock.release()
    
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
motor1 = AdvanceOrientalMotor()
motor1.enable()
motor1.set_expectedSpeed(1)
#motor1.set_position(5)
#motor1.set_pos_mode_expectedSpeed(-2)
time.sleep(2)
motor1.stop()
start = time.time()
#motor1.position_move()
print time.time()-start
#motor1.stop()
"""
