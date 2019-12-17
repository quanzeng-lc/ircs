#!/usr/bin/env python
# encoding: utf-8

import threading
import time
import sys
from enum import Enum
import serial.tools.list_ports
from RCPContext.RCPContext import RCPContext
from RCPControl.Motor.AdvanceOrientalMotor import AdvanceOrientalMotor
from RCPControl.Motor.AngioOrientalMotor import AngioOrientalMotor
from RCPControl.Motor.RotateOrientalMotor import RotateOrientalMotor
from RCPControl.Motor.CatheterOrientalMotor import CatheterOrientalMotor
from RCPControl.Gripper import Gripper
from RCPControl.MaxonMotor import MaxonMotor
from RCPControl.InfraredReflectiveSensor import InfraredReflectiveSensor
from RCPControl.EmergencySwitch import EmergencySwitch
from RCPCom.FeedbackMsg import FeedbackMsg
from RCPControl.SensingParameter import SensingParameter
from RCPControl.GlobalParameterType import GlobalParameterType
from RCPControl.Feedback import Feedback
FORCEFEEDBACK = 6


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
        self.guidewireProgressHome = False
	# ---------------------------------------------------------------------------------------------
	# execution units of the interventional robot
	# ---------------------------------------------------------------------------------------------
        self.guidewireProgressMotor = AdvanceOrientalMotor()
        self.guidewireProgressMotor.open_device()
        self.guidewireProgressMotor.setParameterTypeID(GlobalParameterType.TRANSLATIONVELOCITY)
        self.guidewireProgressMotor.open_device()
        self.guidewireRotateMotor = RotateOrientalMotor()
        self.guidewireRotateMotor.setParameterTypeID(GlobalParameterType.ROTATIONVELOCITY)
        self.guidewireRotateMotor.open_device()
        self.catheterMotor = CatheterOrientalMotor()
        self.catheterMotor.open_device()
        self.angioMotor = AngioOrientalMotor()
        self.angioMotor.open_device()
        self.gripperFront = Gripper(7)
        self.gripperBack = Gripper(8)
	
	# ---------------------------------------------------------------------------------------------
        # sensors
        # ---------------------------------------------------------------------------------------------
        self.infraredReflectiveSensor = InfraredReflectiveSensor()

        # --------------------------------------------------------------
        # feedback
        #
        # -------------------------------------------------------------
        portList = list(serial.tools.list_ports.comports())
        portListUSB = list()
        if len(portList) == 0:
            print("no serial port found")
        else:
            for i in range(0, len(portList)):
                port = list(portList[i])[0]
                portListUSB.append(port)
        #print len(portListUSB)
        self.forceFeedback = Feedback(portListUSB[0], 9600, 8, 'N', 1, self.context)
        self.torqueFeedback = Feedback(portListUSB[1], 9600, 8, 'N', 1, self.context)
        self.forceFeedback.setID(GlobalParameterType.FORCEFEEDBACK)
        self.torqueFeedback.setID(GlobalParameterType.TORQUEFEEDBACK)
        self.forceFeedback.start()
        self.torqueFeedback.start()

        # ---------------------------------------------------------------------------------------------
        # EmergencySwitch
        # ---------------------------------------------------------------------------------------------
        self.switch = EmergencySwitch()
        self.emSwitch = 1
        self.lastSwitch = 0
        self.em_count = 0

        # ---------------------------------------------------------------------------------------------
        # speed parameters
        # ---------------------------------------------------------------------------------------------
        self.speedProgress = 10 
        self.speedRotate = 60
        self.speedCatheter = 2
        self.rotateTime = 720/self.speedRotate
        self.homeSpeed = 3
        #self.pos_speed = 2
        #self.position_cgf = 1
        #self.position_cgb = 2

	# -------------------------------------------------------------------------
        # real time task to parse commandes in context
        # ---------------------------------------------------------------------------------
        self.dispatchTask = threading.Thread(None, self.do_parse_commandes_in_context)
        self.dispatchTask.start()

#        self.aquirefeedbackTask = threading.Thread(None, self.aquirefeedback_context)
#        self.aquirefeedbackTask.start()
        
    def set_global_state(self, state):
        self.global_state = state	

    def do_parse_commandes_in_context(self):
        """
        determine system's status and start to decode or to close devices  	 
	"""
        """
        while self.flag:            
            if not self.context.get_system_status():
		self.guidewireRotateMotor.close_device()
		self.guidewireProgressMotor.close_device()
		self.catheterMotor.close_device()
		self.angioMotor.close_device()
		sys.exit()
		self.flag = False

		print "system terminated"	
	    else:
                self.emSwitch = self.switch.read_current_state()
                #emergency status switch  
                if self.emSwitch == 1:
                    time.sleep(0.02)
                    self.guidewireRotateMotor.standby()
                    self.guidewireProgressMotor.standby()
                    self.catheterMotor.standby()
                    self.angioMotor.standby()
                    self.lastSwitch = 1

                elif self.emSwitch == 0 and self.lastSwitch == 1:
                    self.guidewireRotateMotor.enable()
                    self.guidewireProgressMotor.enable()
                    self.catheterMotor.enable()
                    self.angioMotor.enable()
                    self.lastSwitch = 0
                    if self.decision_making() == 1:
                        self.decode()       

                elif self.emSwitch == 0 and self.lastSwitch == 0:
                    if self.decision_making() == 1:
                        self.decode()

	    time.sleep(0.05)
        """

    def decision_making(self):
        ret = 1
        
        # determine control availability
        #ret = self.context.getGlobalDecisionMade()

        return ret


    def decode(self):
        """
        decode messages in the sequence and performe operations
         """
        self.set_global_state(self.infraredReflectiveSensor.read_current_state())
        # print "status:", self.global_state
        # forward infraredreflection and backward infraredflection are both invalid
        if self.needToRetract == True:
            return
        if self.global_state == 2:
            print("retract")
            self.guidewireProgressMotor.set_expectedSpeed(0)
            self.needToRetract = True
            retractTask = threading.Thread(None, self.push_guidewire_back)
            retractTask.start()
        elif self.global_state == 1:
            # back infraredreflection valid
            print("backlimitation, move forwward")
            if self.guidewireProgressHome == True:
                return
            self.guidewireProgressHome = True
            homeTask = threading.Thread(None, self.push_guidewire_home)
            homeTask.start()
        # forward infraredreflection and backward minfraredreflection are both valid
        elif self.global_state == 3:
            self.guidewireProgressMotor.set_expectedSpeed(0)
            return
 
	# ---------------------------------------------------------------------------------------------
        # catheter execution case
        # ---------------------------------------------------------------------------------------------

        if self.context.get_catheter_move_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_catheter_move_msg()
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            if msg.get_motor_orientation() == 0:
                self.catheterMotor.set_expectedSpeed(msg.get_motor_speed()/40.0)
                return
            elif msg.get_motor_orientation() == 1:
                self.catheterMotor.set_expectedSpeed(-msg.get_motor_speed()/40.0)
                return
	# ---------------------------------------------------------------------------------------------
        # guidewire progress execution case
        # ---------------------------------------------------------------------------------------------
        if not self.needToRetract: # or not self.need ....
            if self.context.get_guidewire_progress_instruction_sequence_length() > 0:
                self.set_global_state(self.infraredReflectiveSensor.read_current_state())
                #print "status:", self.global_state
                # forward infraredreflection and backward infraredflection are both invalid
                if self.global_state == 0:
               	    msg = self.context.fetch_latest_guidewire_progress_move_msg()
                    if self.draw_back_guidewire_curcuit_flag == False:
                        return 
                    if msg.get_motor_orientation() == 0 and abs(msg.get_motor_speed()) < 460:
			#print(-msg.get_motor_speed())
                        self.guidewireProgressMotor.enable()
                        self.guidewireProgressMotor.set_expectedSpeed(-msg.get_motor_speed()/20)
                        self.cptt = 0
                    elif msg.get_motor_orientation() == 1 and abs(msg.get_motor_speed()) < 460:
			#print (msg.get_motor_speed())
                        self.guidewireProgressMotor.enable()
                        self.guidewireProgressMotor.set_expectedSpeed(msg.get_motor_speed()/20)
                    else:
                        self.guidewireProgressMotor.set_expectedSpeed(0)

	# ---------------------------------------------------------------------------------------------
        # guidewire rotate execution case
        # ---------------------------------------------------------------------------------------------    
       	    if self.context.get_guidewire_rotate_instruction_sequence_length() > 0: 
                msg = self.context.fetch_latest_guidewire_rotate_move_msg()
                speed = msg.get_motor_speed()
                position = (msg.get_motor_position()*4000)/360
                if self.draw_back_guidewire_curcuit_flag == False:
                    return             
                if msg.get_motor_orientation() == 0:
                    self.guidewireRotateMotor.set_expectedSpeed(speed/40.0)
                    pass
                elif msg.get_motor_orientation() == 1:
                    self.guidewireRotateMotor.set_expectedSpeed(-speed/40.0)
                    pass
        # ---------------------------------------------------------------------------------------------
        # contrast media push execution case
        # ---------------------------------------------------------------------------------------------
        if self.context.get_contrast_media_push_instruction_sequence_length() > 0:
            msg = self.context.fetch_latest_contrast_media_push_move_msg()
            ret = msg.get_motor_speed()
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            if msg.get_motor_orientation() == 0:
                self.angioMotor.set_expectedSpeed(-ret/40.0)
            elif msg.get_motor_orientation() == 1:
                self.angioMotor.set_expectedSpeed(ret/40.0)

        if self.context.get_retract_instruction_sequence_length() > 0:
            if self.draw_back_guidewire_curcuit_flag == False:
                return 
            self.draw_back_guidewire_curcuit()

        if self.context.get_injection_command_sequence_length() > 0:
            msg = self.context.fetch_latest_injection_msg_msg()
            #print "injection command", msg.get_speed(),msg.get_volume()
	   
            if msg.get_volume() < 0:
                self.angioMotor.set_pos_speed(msg.get_speed()/40.0)
                self.angioMotor.set_position(msg.get_volume()/4.5)
                self.angioMotor.pull_contrast_media()
            elif msg.get_volume() <= 30:
                self.angioMotor.set_pos_speed(msg.get_speed()/40.0)
                self.angioMotor.set_position(msg.get_volume()/4.5)
                self.angioMotor.push_contrast_media()

    def push_contrast_agent(self):
        """
        Contrast agent push
        """
        self.angioMotor.set_pos_speed(self.pos_speed)
        self.angioMotor.set_position(self.position_cgf/4.5)
        self.angioMotor.push_contrast_media()

    def pull_contrast_agent(self):
        self.angioMotor.set_pos_speed(self.pos_speed)
        self.angioMotor.set_position(self.position_cgb/4.5)
        self.angioMotor.pull_contrast_media()


    def push_guidewire_back(self):
        """
        the shifboard get back when guidewire progress
	"""
        #self.context.clear_guidewire_message()
        self.draw_back_guidewire_curcuit_flag == False
        
	#self.gripperFront.gripper_chuck_loosen()
        #self.gripperBack.gripper_chuck_loosen()
        #time.sleep(1)	    
        
	# fasten front gripper
        self.gripperFront.gripper_chuck_fasten()
	
	# self-tightening chunck
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)    
        self.guidewireRotateMotor.set_expectedSpeed(self.speedRotate) # +/loosen
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)
        
        #self.gripperFront.gripper_chuck_loosen()
        #time.sleep(1)
        self.guidewireProgressMotor.set_expectedSpeed(-self.speedProgress)
        #time.sleep(3)
        
            
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state != 1:
            #self.global_state = self.infraredReflectiveSensor.read_current_state()
            #if self.global_state == 4:
                #self.global_state = self.infraredReflectiveSensor.read_current_state()
                #continue
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
            print("retracting", self.global_state)
        print("back limitation arrived")

        self.guidewireProgressMotor.set_expectedSpeed(0)
        self.guidewireRotateMotor.set_expectedSpeed(-self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)

        self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
        self.draw_back_guidewire_curcuit_flag == True
	#self.context.clear_guidewire_message()
        self.needToRetract = False
   
    def push_guidewire_advance(self):
        """
        the shiftboard advance with pushing guidewire
	"""
        #self.context.clear_guidewire_message()
        self.guidewireProgressMotor.set_expectedSpeed(self.speedProgress)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state != 2:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
        #print "pushing", self.global_state
        #print "front limitation arrived"
        self.guidewireProgressMotor.set_expectedSpeed(0)
        #self.guidewireRotateMotor.rm_move_to_position(90, -8000)   
        #time.sleep(4)
    
    def push_guidewire_home(self):
        self.context.clear_guidewire_message()
        self.guidewireProgressMotor.enable()
        self.guidewireProgressMotor.set_expectedSpeed(self.homeSpeed)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state == 1:
            time.sleep(0.5)
            print("home")
            self.global_state = self.infraredReflectiveSensor.read_current_state()
        #print "pushing", self.global_state
        #print "front limitation arrived"

        self.guidewireProgressMotor.set_expectedSpeed(0)
        self.context.clear_guidewire_message()
        self.guidewireProgressHome = False
        #self.guidewireRotateMotor.rm_move_to_position(90, -8000)   
        #time.sleep(4)


    def multitime_push_guidewire(self):
        """
        the process of pushing guidewire for several times
	"""
        self.define_number_of_cycles()
        for i in range (0,self.number_of_cycles):
            self.push_guidewire_advance()
            self.push_guidewire_back()
            print(i)
   
    def draw_guidewire_back(self):
        """
        the shiftboard go back with drawing back guidewire
	"""
        self.guidewireRotateMotor.set_expectedSpeed(self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)
        self.gripperBack.gripper_chuck_loosen()
        time.sleep(1)
        self.guidewireProgressMotor.set_expectedSpeed(-self.speedProgress)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state != 1:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
            #print "retracting", self.global_state
        #print "back limitation arrived"

        self.guidewireProgressMotor.set_expectedSpeed(0)
        #self.guidewireRotateMotor.rm_move_to_position(85, -4000)
        #time.sleep(4)
        #self.draw_back_guidewire_curcuit_flag == True
        #self.needToRetract = False
       

    def chuck_loosen(self):
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        self.guidewireRotateMotor.set_expectedSpeed(-self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewirRotateMotor.set_expectedSpeed(0)

    def chuck_fasten(self):
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        self.guidewireRotateMotor.set_expectedSpeed(self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)

    def draw_guidewire_advance(self):
        """
        the shiftboard advance in the process of drawing back of guidewire
	"""
        self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
        time.sleep(1)
        self.gripperFront.gripper_chuck_fasten()
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        self.guidewireRotateMotor.set_expectedSpeed(-self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)
        self.guidewireProgressMotor.set_expectedSpeed(self.speedProgress)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state !=2:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
        #print "advancing", self.global_state
        #print "front limitation arrived"
       
        self.guidewireProgressMotor.set_expectedSpeed(0)
        #self.gripperFront.gripper_chuck_fasten()
        #self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        #self.guidewireRotateMotor.rm_move_to_position(80, -4000)
        #time.sleep(3)
       
        #self.gripperFront.gripper_chuck_fasten()
        #time.sleep(1)
	#self.gripperFront.gripper_chuck_loosen()
        #self.gripperBack.gripper_chuck_loosen()
	#time.sleep(1)
             
    def multitime_draw_back_guidewire(self):
        """
        the process of drawing back guidewire for several times
	"""
        self.define_number_of_cycles()
        for i in range (0,self.number_of_cycles):
            self.draw_guidewire_advance()
            self.draw_guidewire_back()
            print(i)
    
    def automatic_procedure(self):
        self.angioMotor.set_pos_speed(4)
        self.angioMotor.set_position(10)
        self.angioMotor.push_contrast_media()
        print("angiographing finish")
        time.sleep(5)
        self.multitime_push_guidewire()

    def push_and_pull(self):
        """
        the test of processing and drawing back guidewire for several times
	"""
        self.multitime_push_guidewire()
        self.multitime_draw_back_guidewire()

    def loosen(self):
        """
        the test of gripper
	"""
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        self.gripperBack.gripper_chuck_loosen()
       #self.gripperBack.gripper_chuck_loosen()
        time.sleep(1)        
   
    def catheter_advance(self):
        """
        the process of guidewire and cathter advance by turns
	"""
        self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
        self.draw_back_guidewire_curcuit_flag == True
        self.needToRetract = False

        self.guidewireProgressMotor.set_expectedSpeed(self.speedProgress)
        self.catheterMotor.set_expectedSpeed(self.speedCatheter)
        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state !=2:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
        #print "pushing", self.global_state
        #print "front limitation arrived"

        self.guidewireProgressMotor.set_expectedSpeed(0)
        self.catheterMotor.set_expectedSpeed(0)
        #self.guidewireRotateMotor.rm_move_to_position(90, -8000)
        #time.sleep(4)
       
        #self.context.clear()
        self.draw_back_guidewire_curcuit_flag == False

        #self.gripperFront.gripper_chuck_loosen()
        #self.gripperBack.gripper_chuck_loosen()
        #time.sleep(1)

        # fasten front gripper
        self.gripperFront.gripper_chuck_fasten()

        # self-tightening chunck
        self.gripperBack.gripper_chuck_fasten()
        time.sleep(1)
        self.guidewireRotateMotor.set_expectedSpeed(-self.speedRotate) # +/loosen
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)

        #self.gripperFront.gripper_chuck_loosen()
        #time.sleep(1)
        self.guidewireProgressMotor.set_expectedSpeed(-self.speedProgress)

        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state != 1:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
            print("retracting", self.global_state)
        print("back limitation arrived")

        self.guidewireProgressMotor.set_expectedSpeed(0)
        self.guidewireRotateMotor.set_expectedSpeed(self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)

    def multitime_catheter_advance(self):
        """
        the process of guidewire and cathter advance by turns for several times
	"""
        self.define_number_of_cycles()
        for i in range (0,self.number_of_cycles):
            self.catheter_advance()
            #print(i)
        
    def test(self):
        self.gripperBack.gripper_chuck_fasten()
   
    def catheter_back(self):
        """
        the process of guidewire and cathter  by turns for several times
	"""
        self.define_number_of_cycles()
        for i in range (0,self.number_of_cycles):
            self.draw_guidewire_back()
            self.catheterMotor.set_expectedSpeed(self.speedCatheter)
            print(i)
    
    def initialization(self):
        """
        the initialization of the status of robot
	"""
        self.draw_back_guidewire_curcuit_flag == False

        #self.gripperFront.gripper_chuck_loosen()
        #self.gripperBack.gripper_chuck_loosen()
        #time.sleep(3)

        # fasten front gripper
       # self.gripperFront.gripper_chuck_fasten()

        # self-tightening chunck
       # self.gripperBack.gripper_chuck_fasten()
       # time.sleep(1)
       # self.guidewireRotateMotor.rm_move_to_position(90, 4000) # +/loosen
       # time.sleep(3)

        #self.gripperFront.gripper_chuck_loosen()
        #time.sleep(1)
        self.guidewireProgressMotor.set_expectedSpeed(-self.speedProgress)

        self.global_state = self.infraredReflectiveSensor.read_current_state()
        while self.global_state != 1:
            time.sleep(0.5)
            self.global_state = self.infraredReflectiveSensor.read_current_state()
            print("retracting", self.global_state)
        print("back limitation arrived")

        self.guidewireProgressMotor.set_expectedSpeed(0)
        self.guidewireRotateMotor.set_expectedSpeed(self.speedRotate)
        time.sleep(self.rotateTime)
        self.guidewireRotateMotor.set_expectedSpeed(0)

        self.gripperFront.gripper_chuck_loosen()
        self.gripperBack.gripper_chuck_loosen()
        self.draw_back_guidewire_curcuit_flag == True
        self.needToRetract = False

    def catheter(self):
        self.catheterMotor.set_expectedSpeed(self.speedCatheter)
     
    def define_number_of_cycles(self):
        """
        define the number of cycels of the robot operation
	"""
        self.number_of_cycles = input("please input the number of cycles")
	
    """
    def aquirefeedback_context(self):
        while True:
            feedbackMsg = FeedbackMsg()
            forcevalue = self.forceFeedback.aquireForce()
            torquevalue = self.torqueFeedback.aquireForce()
            
            forcedirection = 0
            if forcevalue < 0:
                forcedirection = 1
            else:
                forcedirection = 0
            forcevalue = abs(forcevalue)
            
            torquedirection = 0
            if torquevalue < 0:
                torquedirection = 1
            else:
                torquedirection = 0
            torquevalue = abs(torquevalue)
            
            feedbackMsg.set_force_direction(forcedirection)
            feedbackMsg.set_force_value(forcevalue)
            feedbackMsg.set_torque_direction(torquedirection)
            feedbackMsg.set_torque_value(torquevalue)
            self.context.append_latest_forceFeedback_msg(feedbackMsg)
            #print("data", forcevalue, torquevalue)
        """

# test push guidewire automatically for several times"
"""
import sys        
dispatcher =  Dispatcher(1, 1)
dispatcher.multitime_push_guidewire()
"""
# test guidewire and cahteter advance by turns
"""
import sys
dispatcher =  Dispatcher(1, 1)
dispatcher.multitime_catheter_advance()
"""
# test injection of contrast media and push guidewire automatically for several times
"""
import sys
dispatcher =  Dispatcher(1, 1)
dispatcher.automatic_procedure()
"""
# test draw_back catheter"
"""
import sys
dispatcher =  Dispatcher(1, 1)
dispatcher.catheter()
"""
#draw back guidewire
"""
import sys
dispatcher =  Dispatcher(1, 1)
dispatcher.multitime_draw_back_guidewire()
"""
# test initialization of robot"
"""
import sys
dispatcher =  Dispatcher(1, 1)
dispatcher.initialization()
"""
# test of gripper
"""
import sys
dispatcher =  Dispatcher(1, 1)
self.gripperFront.gripper_chuck_loosen()
"""
# test of motor
"""
import sys
dispatcher =  Dispatcher(1, 1)
dispatcher.guidewireProgressMotor.set_expectedSpeed(400)
time.sleep(2)
dispatcher.guidewireProgressMotor.set_expectedSpeed(0)
"""

# test of contrast agent
"""
import sys
dispatcher = Dispatcher(1, 1)
dispatcher.push_contrast_agent()
#dispatcher.pull_contrast_agent()
"""
