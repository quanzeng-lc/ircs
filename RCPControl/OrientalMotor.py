#!/usr/bin/env python
# encoding: utf-8

#import RPi.GPIO as GPIO
import time
import threading


class OrientalMotor(object):
    def __init__(self, push_io, pull_io, mode_flag):
        
        self.orientalMotorPushLock = threading.Lock()
        self.orientalMotorPullLock = threading.Lock()
#       self.orientalMotorPositionPushLock = threading.Lock()
#	self.orientalMotorPositionPullLock = threading.Lock()

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.flag = True
	self.pos_flag = True
        self.speedFlag = 0
        self.count = 0
        self.pushIO = push_io
        self.pullIO = pull_io
        GPIO.setup(self.pushIO, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.pullIO, GPIO.OUT, initial=GPIO.HIGH)


	#mode choose
	self.mode = mode_flag

        #velocity mode
        self.speed = 0

        #position mode
        self.pos_motor_flag = 1
	self.re_vol_pos = 1    # 3.4
        self.position = 0
	self.re_volsp_possp = 204.0
        self.pos_speed = 60.0
	
	self.pos_count = 0
#	self.all_sleep_time = 0
        
        self.mv_enable = True

	if self.mode:
	    self.moveTask = threading.Thread(None, self.continuous_move)
            self.moveTask.start()
#	else:
#	    self.moveTask = threading.Thread(None, self.continuous_move_position)
#            self.moveTask.start()


    def open_device(self):
        self.flag = True

    def close_device(self):
	self.flag = False

    def close_position_device(self):
	self.pos_flag = False

    def set_speed(self, speed):
        if speed > 0:
            self.speedFlag = 1
        elif speed < 0:
            self.speedFlag = 2
#        self.speed = abs(speed)        
        elif speed == 0:
	    self.speedFlag = 0
#	    self.flag = False
#            self.speed = 1
        self.speed = abs(speed)
   
    def standby(self):
        self.mv_enable = False
    
    def enable(self):
        self.mv_enable = True

    def continuous_move(self):
        while self.flag:            
            if self.mv_enable:
                if self.speedFlag == 0:
		    time.sleep(0.1)

                if self.speedFlag == 1:
                    self.push()
            
                if self.speedFlag == 2:
                    self.pull()
            else:
                time.sleep(0.5)

	    
    def rtz(self):
        GPIO.output(self.pushIO, True)
        GPIO.output(self.pullIO, True)
    
    def push(self):
        self.orientalMotorPushLock.acquire()
#	interval = 0.0005*60/self.speed
	if self.speed == 0:
	    interval = 0
	else:
            interval = 0.0005*60/self.speed
        GPIO.output(self.pushIO, False)              
        time.sleep(interval)                
        GPIO.output(self.pushIO, True)
        time.sleep(interval)
        self.count += 1
        self.orientalMotorPushLock.release()

    def pull(self):
        self.orientalMotorPullLock.acquire()
	if self.speed == 0:
            interval = 0
        else:
            interval = 0.0005*60/self.speed
        GPIO.output(self.pullIO, False)
        time.sleep(interval)
        GPIO.output(self.pullIO, True)
        time.sleep(interval) 
        self.count += 1
        self.orientalMotorPullLock.release()


    #Position Mode    #############################1
    def set_position(self, volume):
        self.position = volume*self.re_vol_pos*2
#	print self.position
#	self.pos_count+= self.position

    def set_pos_speed(self, vol_speed):
        self.pos_speed = vol_speed*self.re_volsp_possp
#	print self.pos_speed
        
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
    
    def push_contrast_media(self):
	self.position_push()
	self.pos_count+= self.position/self.re_vol_pos	
        time.sleep(0.001)

    def pull_contrast_media(self):
        self.position_pull()


    def pull_back(self):
#	self.idt_motor()
#	print self.pos_count#######################################2
	self.set_position(self.pos_count/2)
#	print self.pos_speed
	self.set_pos_speed(self.pos_speed/self.re_volsp_possp/2)
	self.position_pull()
#	print self.get_position_count_sleep_time()
#	time.sleep(self.get_position_count_sleep_time())
#	print self.get_position_count_sleep_time()
	self.stop()

    def stop(self):
	self.set_position(0)
	self.set_pos_speed(0)
	self.position_pull()
	time.sleep(0.01)
	self.pos_count = 0

    def idt_motor(self):    #identify the motor type
        #if advancement motor, pos_motor_flag=4;
        if self.pushIO == 20 and self.pullIO == 21:
            self.pos_motor_flag = 4

        #if catheterMotor, pos_motor_flag=??
        if self.pushIO == 14 and self.pullIO == 15:
            self.pos_motor_flag = 1

        #if angioMotor, pos_motor_flag=??
        if self.pushIO == 23 and self.pullIO == 24:
            self.pos_motor_flag = 1
    
    def position_push(self):
#	self.orientalMotorPositionPushLock.acquire()
        self.idt_motor()
#	print self.pos_motor_flag
        if self.position == 0 or self.pos_speed == 0:
            distance = 0
	    interval = 0
	else:
            distance = int(1000*self.position/self.pos_motor_flag)
	    interval = 0.0005*60/self.pos_speed*self.pos_motor_flag
#	print distance
#	print interval
        for i in range(0, distance): 
            GPIO.output(self.pushIO, False)              
            time.sleep(interval)                
            GPIO.output(self.pushIO, True)
            time.sleep(interval)
#            self.count += 1
#	self.orientalMotorPositionPushLock.release()

            
    def position_pull(self):
#	self.orientalMotorPositionPullLock.acquire()
        self.idt_motor()
	if self.position == 0 or self.pos_speed == 0:
            distance = 0
            interval = 0
        else:
            distance = int(abs(1000*self.position/self.pos_motor_flag))
            interval = 0.0005*60/self.pos_speed*self.pos_motor_flag
#	print distance
        for i in range(0, distance):
            GPIO.output(self.pullIO, False)              
            time.sleep(interval)             
            GPIO.output(self.pullIO, True)
            time.sleep(interval)
#            self.count += 1
#	self.orientalMotorPositionPullLock.release()

    def get_position_sleep_time(self):
	if self.position == 0 or self.pos_speed == 0:
	    return 0.001
	else:
#	    self.all_sleep_time+= abs(self.position*60/self.pos_motor_flag/self.pos_speed)
	    return abs(self.position*60/self.pos_speed)


    def get_position_count_sleep_time(self):
        if self.pos_count == 0 or self.pos_speed == 0:
            return 0.001
        else:
#	    print self.pos_count, self.pos_speed
            return abs(self.pos_count*self.re_vol_pos*60/self.pos_speed)

"""
motor1 = OrientalMotor(23, 24, False)
motor1.set_position(2.5)
motor1.set_pos_speed(10)
start = time.time()
motor1.push_contrast_media()
print time.time()-start
#motor1.stop()
"""
