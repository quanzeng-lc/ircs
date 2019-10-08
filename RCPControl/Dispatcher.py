#!/usr/bin/env python
# encoding: utf-8

import threading
import time
import sys
from RCPContext.RCPContext import RCPContext
from OrientalMotor import OrientalMotor
#from Gripper import Gripper
from MaxonMotor import MaxonMotor
from InfraredReflectiveSensor import InfraredReflectiveSensor
#from EmergencySwitch import EmergencySwitch
TRANS_EFFICIENT = float(2*16)/(529*60)

class Dispatcher(object):
    """
        description:this class plays an role in th command and control of the interventional robot which includes:
                         -- the control of GPIOs of the raspberryPi which connet motors, sensors and grippers
                         -- the distribution of tasks in different threads
                         -- the command and control of the actions of interventional robot in surgery   
	author:Cheng WANG
    """
    def __init__(self, context, local_mode=0):
        self.context = context

	# ---------------------------------------------------------------------------------------------
        # initialisation
        # ---------------------------------------------------------------------------------------------
	self.flag = True
	self.cptt = 0
        self.global_state = 0
	self.needToRetract = False
        self.draw_back_guidewire_curcuit_flag = True
        self.number_of_cycles = 0
	# ---------------------------------------------------------------------------------------------
	# execution units of the interventional robot
	# ---------------------------------------------------------------------------------------------
        self.frontNeedleMotor = MaxonMotor(2, "EPOS2", "MAXON SERIAL v2", "USB", "USB0", 1000000)
        self.backNeedleMotor = MaxonMotor(1, "EPOS2", "MAXON SERIAL V2", "USB", "USB1", 1000000)
	
	# ---------------------------------------------------------------------------------------------
        # TODO : haptic sensors
        self.feedback_sensor = Feedback("/dev/ttyUSB0", 9600, 8, 'N', 1)
        # --------------------
        # self.hapticSensor = HapticSensor()

        # ---------------------------------------------------------------------------------------------
        # speed parameters
        # ---------------------------------------------------------------------------------------------
        self.speedProgress = 1000 
        self.speedRotate = 60
        self.speedCatheter =10
        self.rotateTime = 180/self.speedRotate

        self.pos_speed = 5
        self.position_cgf = 2
        self.position_cgb = -100

	# ---------------------------------------------------------------------------------------------
        # real time task to parse commandes in context
        # ---------------------------------------------------------------------------------------------
	if local_mode == 0:
       	    self.dispatchTask = threading.Thread(None, self.do_parse_commandes_in_context)
       	    self.dispatchTask.start()

        #real force feedback
        self.forcefeedbackTask = threading.Thread(None, self.aquireForceFeedback)
        self.forcefeedbackTask.start()

        
    def set_global_state(self, state):
	self.global_state = state	

    def do_parse_commandes_in_context(self):
	"""
        determine system's status and start to decode or to close devices  	 
	"""
        while self.flag:            
            if not self.context.get_system_status():
		self.frontNeedleMotor.close_device()
		self.backNeedleMotor.close_device()
		self.flag = False

		print "system terminated"	
	    else:
                self.decode()
                
	    time.sleep(0.02)
	    
    def decode(self):
	"""
        decode messages in the sequence and performe operations
        """ 
	# ---------------------------------------------------------------------------------------------
        # catheter execution case
        # ---------------------------------------------------------------------------------------------
      	if self.context.get_catheter_move_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_catheter_move_msg()
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            realTargetVelocity = int((10.0*msg.get_motor_speed())/(200*TRANS_EFFICIENT))
            if msg.get_motor_orientation() == 1: # rm_move_to_position(400,8000*50)
		self.frontNeedleMotor.rm_move(-realTargetVelocity)
                return
            elif msg.get_motor_orientation() == 0:
#                self.frontNeedleMotor.rm_move_to_position(-msg.get_motor_speed(), 8000)
		self.frontNeedleMotor.rm_move(realTargetVelocity)
                return
        elif self.context.get_guidewire_progress_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_guidewire_progress_move_msg()
            if msg.get_motor_orientation() == 1: 
                self.backNeedleMotor.rm_move(-msg.get_motor_speed()*5)
                return
            elif msg.get_motor_orientation() == 0:
                self.backNeedleMotor.rm_move(msg.get_motor_speed()*5)
                return

    def aquireForceFeedback(self):
        forcefeedback = self.feedback_sensor.aquireForce()
        forcefeedbackMsg = FeedbackMsg() 
        direction = 0
        forcevalue = 0
        if forcefeedback > 0:
            direction = 0
            forcevalue = forcefeedback
        else:
            direction = 1
            forcevalue = - forcefeedback
        forcefeedbackMsg.set_force_type(0)
        forcefeedbackMsg.set_force_direction(direction)
        forcefeedbackMsg.set_force_value(forcefeedback)

        self.context.append_latest_forcefeedback_message(forcefeedbackMsg)








