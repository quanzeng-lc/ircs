#!/usr/bin/env python
# encoding: utf-8
import threading
from enum import Enum
#from RCPControl.Feedback import Feedback
#from OrientalMotor import OrientalMotor

# --------------------------------------
# T timestamps
# Ft(t) Translation Force
# Fr(t) Rotation Force
# Lc(t) distance from chuck to catheter  Expected
# Lt(t) length of telescopic rod 
# Lcg(t) distance from catheter end to guidewire end 
# Wr(t) Translation guidewire angle Expected
# V(t) Translation Velocity
# W(t) Roattion Velocity
# Bid(t) Branch ID
# --------------------------------------
"""
class GlobalParameterType(Enum):
    FORCEFEEDBACK = 1
    TORQUEFEEDBACK = 2
    DISTANCEFROMCHUCKTOCATHETER = 3
    TELESCOPICRODLENGTH = 4
    DISTANCEFROMCATHETERTOGUIDEWIRE = 5
    GUIDEWIREANGLE = 6
    TRANSLATIONVELOCITY = 7
    ROTATIONVELOCITY = 8
"""

class SensingParameter(object):
    def __init__(self):
        self.timestamps = 0
        self.forceFeedback = 0.0
        self.torqueFeedback = 0.0
        self.distanceFromChuckToCatheter = 0.0
        self.telescopicRodLength = 0.0
        self.distanceFromCatheterToGuidewire = 0.0
        self.guidewireAngle = 0.0
        self.translationVelocity = 0.0
        self.rotationVelocity = 0.0

    def setTimestamps(self, timestamps):
        self.timestamps = timestamps 
    
    def getTimestamps(self):
        return self.timestamps  

    def setForceFeedback(self, forceFeedback):
        self.forceFeedback = forceFeedback  
    
    def getForceFeedback(self):
        return self.forceFeedback  

    def setTorqueFeedback(self, torqueFeedback):
        self.torqueFeedback = torqueFeedback
    
    def getTorqueFeedback(self):
        return self.torqueFeedback

    def setDistanceFromChuckToCatheter(self, distanceFromChuckToCatheter):
        self.distanceFromChuckToCatheter = distanceFromChuckToCatheter 
    
    def getDistanceFromChuckToCatheter(self):
        return self.distanceFromChuckToCatheter 

    def setTelescopicRodLength(self, telescopicRodLength):
        self.timestamps = telescopicRodLength 
    
    def getTelescopicRodLength(self):
        return self.telescopicRodLength  

    def setDistanceFromCatheterToGuidewire(self, distanceFromCatheterToGuidewire):
        self.distanceFromCatheterToGuidewire = distanceFromCatheterToGuidewire 
    
    def getDistanceFromCatheterToGuidewire(self):
        return self.distanceFromCatheterToGuidewire 

    def setGuidewireAngle(self, guidewireAngle):
        self.guidewireAngle = guidewireAngle 
    
    def getGuidewireAngle(self):
        return self.guidewireAngle  

    def setTranslationVelocity(self, translationVelocity):
        self.translationVelocity = translationVelocity 
    
    def getTranslationVelocity(self):
        return self.translationVelocity  

    def setRotationVelocity(self, rotationVelocity):
        self.rotationVelocity = rotationVelocity 
    
    def getRotationVelocity(self):
        return self.rotationVelocity  

