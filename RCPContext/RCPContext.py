#-*- coding: utf-8 -*-
import threading
import time
from threading import Lock
import csv
from RCPControl.SensingParameter import SensingParameter
from RCPControl.GlobalParameterType import GlobalParameterType

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
  
        # forcefeedback
        self.forcefeedbackSequence = []
        
        # push catheter and guidewire together
        self.catheter_guidewire_push_sequence = []

	# system control
        self.closeSessionSequence = []
        

        self.sensingParameterSequence = []

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
        self.globalContrastMediaVolumn = 0

        self.globalForceFeedback = 0.0
        self.globalTorqueFeedback = 0.0
        self.globalDistanceFromChuckToCatheter = 0.0
        self.globalTelescopicRodLength = 0.0
        self.globalDistanceFromCatheterToGuidewire = 0.0
        self.globalGuidewireAngle = 0.0
        self.globalTranslationVelocity = 0.0
        self.globalRotationVelocity = 0.0
        self.globalDecisionMade = 1

        informationAnalysisTask = threading.Thread(None, self.coreInformationAnalysis)
        informationAnalysisTask.start()

        decisionMaking_task = threading.Thread(None, self.decisionMaking)
        decisionMaking_task.start()

        self.storingDataLock = Lock()
        storingDataTask = threading.Thread(None, self.storingData)
        storingDataTask.start()

    def coreInformationAnalysis(self):
        while True:
            parameter = SensingParameter()
            parameter.setTimestamps(10)
            parameter.setForceFeedback(self.globalForceFeedback)
            parameter.setTorqueFeedback(self.globalTorqueFeedback)
            parameter.setDistanceFromChuckToCatheter(10)
            parameter.setTelescopicRodLength(10)
            parameter.setDistanceFromCatheterToGuidewire(10)
            parameter.setGuidewireAngle(10)
            parameter.setTranslationVelocity(10)
            parameter.setRotationVelocity(10)
            self.sensingParameterSequence.append(parameter)
            #print 'length',len(self.sensingParameterSequence)
            #print "forcefeedback ", parameter.getForceFeedback(), "torquefeedback ", parameter.getTorqueFeedback()
            time.sleep(0.03)

    def decisionMaking(self):
        while True:

            self.globalDecisionMade = 1
            time.sleep(0.01)
        #return ret

    def decision_made(self):
        ret = self.decision_made
        return ret

    def storingData(self):
        while True:
            data = list()
            self.storingDataLock.acquire()
            if len(self.sensingParameterSequence) >= 100:
                data = self.sensingParameterSequence[0:100]
                del self.sensingParameterSequence[0:100]
            self.storingDataLock.release() 
            path = "./hapticData/hapticFeedback.csv"
            for var in data:
                tmpData = list()
                tmpData.append(str(var.getTimestamps()))
                tmpData.append(str(var.getForceFeedback()))
                tmpData.append(str(var.getTorqueFeedback()))
                tmpData.append(str(var.getDistanceFromChuckToCatheter()))
                tmpData.append(str(var.getTelescopicRodLength()))
                tmpData.append(str(var.getDistanceFromCatheterToGuidewire()))
                tmpData.append(str(var.getGuidewireAngle()))
                tmpData.append(str(var.getTranslationVelocity()))
                tmpData.append(str(var.getRotationVelocity()))
               # for x in tmpData:
                #    print x
                with open(path, 'a+') as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(tmpData)
                    #f.write(tmpData[0])

            time.sleep(1)

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

    def getGlobalForceFeedback(self):
        return self.globalForceFeedback

    def setGlobalForceFeedback(self, globalForceFeedback):
        self.globalForceFeedback = globalForceFeedback

    def getGlobalTorqueFeedback(self):
        return self.globalTorqueFeedback

    def setGlobalTorqueFeedback(self, globalTorqueFeedback):
        self.globalTorqueFeedback = globalTorqueFeedback

    def getGlobalDistanceFromChuckToCatheter(self):
        return self.globalDistanceFromChuckToCatheter

    def setGlobalDistanceFromChuckToCatheter(self, globalDistanceFromChuckToCatheter):
        self.globalDistanceFromChuckToCatheter = globalDistanceFromChuckToCatheter

    def getGlobalTelescopicRodLength(self):
        return self.globalTelescopicRodLength

    def setGlobalTelescopicRodLength(self, globalTelescopicRodLength):
        self.globalTelescopicRodLength = globalTelescopicRodLength

    def getGlobalDistanceFromCatheterToGuidewire(self):
        return self.globalDistanceFromCatheterToGuidewire

    def setGlobalDistanceFromCatheterToGuidewire(self, globalDistanceFromCatheterToGuidewire):
        self.globalDistanceFromCatheterToGuidewire = globalDistanceFromCatheterToGuidewire

    def getGlobalGuidewireAngle(self):
        return self.globalGuidewireAngle

    def setGlobalGuidewireAngle(self, globalGuidewireAngle):
        self.globalGuidewireAngle = globalGuidewireAngle

    def getGlobalTranslationVelocity(self):
        return globalTranslationVelocity

    def setGlobalTranslationVelocity(self, globalTranslationVelocity):
        self.globalTranslationVelocity = globalTranslationVelocity

    def getGlobalRotationVelocity(self):
        return self.globalRotationVelocity

    def setGlobalRotationVelocity(self, globalRotationVelocity):
        self.globalRotationVelocity = globalRotationVelocity

    def setGlobalRotationVelocity(self, globalRotationVelocity):
        self.globalRotationVelocity = globalRotationVelocity

    def getGlobalDecisionMade(self):
        ret = self.globalDecisionMade
        return ret

    def setGlobalParameter(self, ID, parameter):
        if ID is GlobalParameterType.FORCEFEEDBACK:
            self.setGlobalForceFeedback(parameter)
        elif ID is GlobalParameterType.TORQUEFEEDBACK:
            self.setGlobalTorqueFeedback(parameter)
        elif ID is GlobalParameterType.DISTANCEFROMCHUCKTOCATHETER:
            self.setGlobalDistanceFromChuckToCatheter(parameter)
        elif ID is GlobalParameterType.TELESCOPICRODLENGTH:
            self.setGlobalTelescopicRodLength(parameter)
        elif ID is GlobalParameterType.DISTANCEFROMCATHETERTOGUIDEWIRE:
            self.setGlobalDistanceFromCatheterToGuidewire(parameter)
        elif ID is GlobalParameterType.GUIDEWIREANGLE:
            self.setGlobalGuidewireAngle(parameter)
        elif ID is TRANSLATIONVELOCITY:
            self.setGlobalTranslationVelocity(parameter)
        elif ID is GlobalParameterType.ROTATIONVELOCITY:
            self.setGlobalRotationVelocity(parameter)
        else:
            print("ParameterType error")

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


    # -------------------------------------------------
    # catheter and guidewire push together
    # --------------------------------------------------
    def get_catheter_guidewire_push_sequence_length(self):
        self.inputLock.acquire()
        length = len(self.catheter_guidewire_push_sequence)
        self.inputLock.release()
        return length

    def get_fetch_latest_catheter_guidewire_push_msg(self):
        self.inputLock.acquire()
        length = len(self.catheter_guidewire_push_sequence)
        ret = self.catheter_guidewire_push_sequence.pop(length - 1)
        self.input.release()
        return ret
