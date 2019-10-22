#-*- coding: utf-8 -*-
import threading


class RCPContext:

    def __init__(self):
	
	# ---------------------------------------------------------------------------------------------
        # define the mutex to avoid concurency
        # ---------------------------------------------------------------------------------------------
        self.inputLock = threading.Lock()
        self.outputLock = threading.Lock()
        
	# ---------------------------------------------------------------------------------------------
        # message sequences
        # ---------------------------------------------------------------------------------------------
	# catheter control commandes in speed mode
	self.catheterMoveInstructionSequence = []
	
	# guidewire control commandes in speed mode
        self.guidewireProgressInstructionSequence = []
        self.guidewireRotateInstructionSequence = []

	# guidewire control commandes in position mode
	self.guidewireMovingDistance = []

	# to be verified...
        self.contrastMediaPushInstructionSequence = []
	self.injectionCommandSequence = []
        self.retractInstructionSequence = []
   
        self.forcefeedbackSequence = []
        
	# system control
	self.closeSessionSequence = []

	# ---------------------------------------------------------------------------------------------
        # system status variable 
        # ---------------------------------------------------------------------------------------------
	self.systemStatus = True
        
        # ------------------------------------------------------------------------------------------------------------
        # control variables:
        #
        # guidewireControlState
        #  where 
        #      0: uncontrolled,
        #      1: valid, 
        #      2: nonvalid_prepare_for_push, 
        #      3: nonvalid_prepare_for_drawn,
        #      4: exception
        #
        # catheterControlState
        #   where
        #      0: uncontrolled,
        #      1: valid
        #      2: nonvalid_beyond_guidewire
        #      3: exception
        # contrastMediaControlState
        #   where
        #      0: uncontrolled,
        #      1: valid
        #      2: exception

        self.guidewireControlState = 0
        self.catheterControlState = 0
        self.contrastMediaControlState = 0

        self.globalGuidewireDistance = 0
        self.globalGuidewireAngle = 0
        self.globalCatheterDistance = 0
        self.globalContrastMediaVolumn = 0
    
    def clear_guidewire_message(self):
        self.guidewireProgressInstructionSequence = []

    def get_guidewire_control_state(self):
        return self.guidewireControlState

    def set_guidewire_control_state(self, guidewire_state):
        self.guidewireControlState = guidewire_state

    def get_catheter_control_state(self):
        return self.catheterControlState

    def set_catheter_control_state(self, catheter_state):
        self.catheterControlState = catheter_state

    def get_contrast_media_control_state(self):
        return self.contrastMediaControlstate

    def set_contrast_media_control_state(self, contrast_media_control_state):
        self.contrastMediaControlState = contrast_media_control_state

    def get_global_guidewire_distance(self):
        return self.globalGuidewireDistance

    def set_global_guidewire_distance(self, guidewire_diatance):
        self.globalGuidewireDiatnce = guidewire_distance

    def get_global_guidewire_angle(self):
        return self.globalGuidewireAngle

    def set_global_guidewire_angle(self, guidewire_angle):
        self.globalGuidewireAngle = guidewire_distance

    def get_global_catheter_distance(self):
        return self.globalCatheterdistance

    def set_global_cather_distance(self, catheter_distance):
        self.globalGuidewireDistance = catheter_distance

    def get_global_contrastmedia_volumn(self):
        return self.globalContrastMediaVolumn

    def set_global_contrastmedia_volumn(self, contrast_media_volumn):
        self.contrast_media_volumn = contrast_media_volumn

    def append_close_session_msg(self, close_session_msg):
	self.closeSessionSequence.append(close_session_msg)
    
    def fetch_close_session_msg(self):
        self.inputLock.acquire()
        length = len(self.closeSessionSequence)
        ret = self.closeSessionSequence.pop(length-1)
        self.inputLock.release()
        return ret
	
    def get_close_session_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.closeSessionSequence)
        self.inputLock.release()
        return length
	
    def append_new_injection_msg(self, msg):
        self.inputLock.acquire()
        self.injectionCommandSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_injection_msg_msg(self):
        self.inputLock.acquire()
        length = len(self.injectionCommandSequence)
        ret = self.injectionCommandSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_injection_command_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.injectionCommandSequence)
        self.inputLock.release()
        return length

    def close_system(self):
	self.systemStatus = False
	
	self.catheterMoveInstructionSequence = []
        self.guidewireProgressInstructionSequence = []
        self.guidewireRotateInstructionSequence = []
        self.contrastMediaPushInstructionSequence = []
        self.retractInstructionSequence = []
        self.guidewireMovingDistance = []
	self.closeSessionSequence = []

    def open_system(self):
	self.systemStatus = True

    def get_system_status(self):
	return self.systemStatus

    def clear(self):
        self.catheterMoveInstructionSequence = []
        self.guidewireProgressInstructionSequence = []
        self.guidewireRotateInstructionSequence = []
        self.contrastMediaPushInstructionSequence = []
        self.retractInstructionSequence = []
        self.guidewireMovingDistance = []
        self.closeSessionSequence = []

    def set_distance(self, dis):
	self.guidewireMovingDistance.append(dis)

    def fetch_latest_guidewire_moving_distance(self):
	self.outputLock.acquire()
        length = len(self.guidewireMovingDistance)
        ret = self.guidewireMovingDistance[length-1]
        self.outputLock.release()
        return ret		

    def fetch_latest_guidewire_moving_distance_msg(self):
        self.outputLock.acquire()
        length = len(self.guidewireMovingDistance)
        ret = self.guidewireMovingDistance.pop(length-1)
        self.outputLock.release()
        return ret

    def get_latest_guidewire_moving_distance_sequence_length(self):
	self.outputLock.acquire()
        length = len(self.guidewireMovingDistance)
        self.outputLock.release()
        return length   
 
    def append_new_catheter_move_message(self, msg):
        self.inputLock.acquire()     
        self.catheterMoveInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_catheter_move_msg(self):
        self.inputLock.acquire()
        length = len(self.catheterMoveInstructionSequence)
        ret = self.catheterMoveInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_catheter_move_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.catheterMoveInstructionSequence)
        self.inputLock.release()
        return length

    def append_new_guidewire_progress_move_message(self, msg):
        self.inputLock.acquire()
        self.guidewireProgressInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_guidewire_progress_move_msg(self):
        self.inputLock.acquire()
        length = len(self.guidewireProgressInstructionSequence)
        ret = self.guidewireProgressInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_guidewire_progress_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.guidewireProgressInstructionSequence)
        self.inputLock.release()
        return length

    def append_new_guidewire_rotate_move_message(self, msg):
        self.inputLock.acquire()
        self.guidewireRotateInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_guidewire_rotate_move_msg(self):
        self.inputLock.acquire()
        length = len(self.guidewireRotateInstructionSequence)
        ret = self.guidewireRotateInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_guidewire_rotate_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.guidewireRotateInstructionSequence)
        self.inputLock.release()
        return length

    def append_new_contrast_media_push_move_message(self, msg):
        self.inputLock.acquire()
        self.contrastMediaPushInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_contrast_media_push_move_msg(self):
        self.inputLock.acquire()
        length = len(self.contrastMediaPushInstructionSequence)
        ret = self.contrastMediaPushInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_contrast_media_push_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.contrastMediaPushInstructionSequence)
        self.inputLock.release()
        return length

    def append_latest_retract_message(self, msg):
        self.inputLock.acquire()
        self.retractInstructionSequence.append(msg)
        self.inputLock.release()

    def fetch_latest_retract_msg(self):
        self.inputLock.acquire()
        length = len(self.retractInstructionSequence)
        ret = self.retractInstructionSequence.pop(length-1)
        self.inputLock.release()
        return ret

    def get_retract_instruction_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.retractInstructionSequence)
        self.inputLock.release()
        return length

    # get forcefeedbqck
    def append_latest_forcefeedback_msg(self, msg):
        self.outputLock.acquire()
        self.forcefeedbackSequence.append(msg)
        self.outputLock.release()

    def fetch_latest_feedback_msg(self):
        self.outputLock.acquire()
        length = len(self.forcefeedbackSequence)
        ret = self.forcefeedbackSequence.pop(length - 1)
        self.outputLock.release()
        return ret

    def get_feedback_sequence_length(self):
        self.outputLock.acquire()
        length = len(self.forcefeedbackSequence)
        self.outputLock.release()
        return length
