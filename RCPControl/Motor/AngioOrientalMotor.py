#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO as GPIO
import time
import threading
from RCPControl.Motor.AdvanceMotor import AdvanceMotor
from RCPContext.RCPContext import RCPContext

# max velocity 10 mm/s
class AngioOrientalMotor(AdvanceMotor):
    def __init__(self):
        
        self.orientalMotorPushLock = threading.Lock()
        self.orientalMotorPullLock = threading.Lock()
#       self.orientalMotorPositionPushLock = threading.Lock()
#	self.orientalMotorPositionPullLock = threading.Lock()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.pushIO = 23
        self.pullIO = 24
        GPIO.setup(self.pushIO, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.pullIO, GPIO.OUT, initial=GPIO.HIGH)
        
        self.context = None

        #parametertype id
        self.hapticFeedbackID = 0

	#mode choose
        self.mode = True

        #velocity mode
        self.expectedSpeed = 0    #mL/s
        self.flag = True
        self.expectedSpeedFlag = 0
        self.count = 0
        # high/low level time interval
        self.velocity_mode_interval = 9999

        # the distance for every circle
        self.dis_circle = 2 #mm
        self.deg_pulse = 0.36 #degree for every pulse
       
        # Syringe diameter
        self.syringe_diameter = 41.2  #mm
        self.pi_efficient = 3.14

        #position mode
        self.pos_motor_flag = 1
        self.pos_flag = True
        self.position = 0
        self.pos_mode_expectedSpeed = 0   # mL/s
        self.pos_mode_expeected_flag = 0
        self.pos_mode_interval = 9999
	
        # actual speed mm/s
        self.actualVelocity = 0

        # count the pulse to calculate the vilocity
        self.pos_count = 0

        # enable
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
        advance_speed = (speed*1000*4) / (self.pi_efficient*self.syringe_diameter*self.syringe_diameter)
        if advance_speed > 0:
            self.expectedSpeedFlag = 1
            self.interval = (self.dis_circle*self.deg_pulse)/(advance_speed*360*2.0)
        elif advance_speed < 0:
            self.expectedSpeedFlag = 2
            self.interval = abs((self.dis_circle*self.deg_pulse)/(advance_speed*360*2.0))
        elif advance_speed == 0:
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
        interval = 0
        if self.expectedSpeed == 0:
            return 
        else:
            interval = self.interval
            #print "interval:", interval
        self.orientalMotorPushLock.release()
        # case where the interval is too large
        if interval > 1:
            return
        GPIO.output(self.pushIO, False)              
        time.sleep(interval)                
        GPIO.output(self.pushIO, True)
        time.sleep(interval)
        self.count += 1

    def pull(self):
        self.orientalMotorPullLock.acquire()
        interval = 0
        if self.expectedSpeed == 0:
            return 
        else:
            interval = self.interval
        self.orientalMotorPullLock.release()
        if interval > 1:
            return
        GPIO.output(self.pullIO, False)
        time.sleep(interval)
        GPIO.output(self.pullIO, True)
        time.sleep(interval) 
        self.count += 1


    #Position Mode    #############################1
    def set_position(self, position):
        advance_distance = (position*1000*4) / (self.pi_efficient*self.syringe_diameter*self.syringe_diameter)
        #print "advance_distance:", advance_distance
        if self.mv_enable == False:
            return
        self.position = position
        self.distance_pulse = int((advance_distance*360)/(self.dis_circle*self.deg_pulse))
	#print self.distance_pulse

    def set_pos_mode_expectedSpeed(self, speed):
        advance_speed = (speed*1000*4) / (self.pi_efficient*self.syringe_diameter*self.syringe_diameter)
        if self.mv_enable == False:
            return
        if speed > 0:
            self.pos_mode_interval = (self.dis_circle*self.deg_pulse)/(advance_speed*360*2.0)
            self.pos_mod_expected_flag = 1
        elif speed < 0:
            self.pos_mode_interval = abs((self.dis_circle*self.deg_pulse)/(advance_speed*360*2.0))
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
#		self.pos_flag = False
            elif self.position < 0:
                self.position_pull()
            elif self.position == 0:
                time.sleep(0.001)
#		self.pos_flag = False

       
    def stop(self):
        self.set_expectedSpeed(0)
        self.set_position(0)
        self.set_pos_mode_expectedSpeed(0)
        time.sleep(0.01)
        self.pos_count = 0

    def position_move(self):
        if self.mv_enable == False:
            return
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
        interval = 0
        if self.position == 0 or self.pos_mode_expectedSpeed == 0:
            distance = 0
            interval = 0
        else:
            distance = self.distance_pulse
            interval = self.pos_mode_interval
            print(distance)
            print(interval)
        for i in range(0, distance): 
            GPIO.output(self.pushIO, False)              
            time.sleep(interval)                
            GPIO.output(self.pushIO, True)
            time.sleep(interval)
    #	self.orientalMotorPositionPushLock.release()

            
    def position_pull(self):
#	self.orientalMotorPositionPullLock.acquire()
        interval = 0
        if self.position == 0 or self.pos_mode_expectedSpeed == 0:
            distance = 0
            interval = 0
        else:
            distance = self.distance_pulse
            interval = self.pos_mode_interval
            print(distance)
            print(interval)
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
motor1 = AngioOrientalMotor()
motor1.enable()
start = time.time()
#motor1.set_position(40)
#motor1.set_pos_mode_expectedSpeed(-5)
motor1.set_expectedSpeed(5)
time.sleep(2)
motor1.stop()
#motor1.position_move()
print time.time()-start
#motor1.stop()
"""
