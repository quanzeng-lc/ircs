from ctypes import *
import time


#Type redefine
BOOL = c_int
DWORD = c_ulong
HANDLE = c_void_p
UINT = c_uint
CHAR = c_char_p
USHORT = c_ushort
LONG = c_long
INT = c_int
TRANS_EFFICIENT = float(2*16)/(529*60)


class MaxonMotor(object):

    #BOOL = c_int
    #DWORD = c_ulong
    #HANDLE = c_void_p
    #UINT = c_uint
    #CHAR = c_char_p
    #USHORT = c_ushort
    #LONG = c_long
    #INT = c_int
    
    def __init__(self, RMNodeId, pDeviceName, pProtocolStackName, pInterfaceName, pPortName, lBaudrate):
        #Type redefine!
        
        self.RMNodeId = USHORT(RMNodeId)
        self.pDeviceName = CHAR(pDeviceName)
        self.pProtocolStackName = CHAR(pProtocolStackName)
        self.pInterfaceName = CHAR(pInterfaceName)
        self.pPortName = CHAR(pPortName)
        self.lBaudrate = UINT(lBaudrate)
        self.RMHandle = HANDLE(0)
        self.errorCode = UINT(0)
        self.lTimeout = UINT(0)

        #self.relativePosition = LONG(relativePosition)
        self.rmPosition = INT(0)
        self.rmVelosity = INT(0)

        self.rotationMotor = cdll.LoadLibrary("libEposCmd.so")

        #Open Device
        self.OpenDevice = self.rotationMotor.VCS_OpenDevice
        self.OpenDevice.argtypes = [CHAR, CHAR, CHAR, CHAR, POINTER(UINT)]
        self.OpenDevice.restype = HANDLE

        #Communication Info
        self.GetProtocolStackSettings = self.rotationMotor.VCS_GetProtocolStackSettings
        self.GetProtocolStackSettings.argtypes = [HANDLE, POINTER(UINT), POINTER(UINT), POINTER(UINT)]
        self.GetProtocolStackSettings.restype = BOOL

        self.SetProtocolStackSettings = self.rotationMotor.VCS_SetProtocolStackSettings
        self.SetProtocolStackSettings.argtypes = [HANDLE, UINT, UINT, POINTER(UINT)]
        self.SetProtocolStackSettings.restype = BOOL

        #Enable Motor
        self.SetEnableState = self.rotationMotor.VCS_SetEnableState
        self.SetEnableState.argtypes = [HANDLE, USHORT, POINTER(UINT)]
        self.SetEnableState.restype = BOOL

        self.GetEnableState = self.rotationMotor.VCS_GetEnableState
        self.GetEnableState.argtypes = [HANDLE, USHORT, POINTER(BOOL), POINTER(UINT)]
        self.GetEnableState.restype = BOOL

        #Clear Fault
        self.GetFaultState = self.rotationMotor.VCS_GetFaultState
        self.GetFaultState.argtypes = [HANDLE, USHORT, POINTER(BOOL), POINTER(UINT)]
        self.GetFaultState.restype = BOOL

        self.ClearFault = self.rotationMotor.VCS_ClearFault
        self.ClearFault.argtypes = [HANDLE, USHORT, POINTER(UINT)]
        self.ClearFault.restype = BOOL

        #Velocity Mode
        self.MoveWithVelocity = self.rotationMotor.VCS_MoveWithVelocity
        self.MoveWithVelocity.argtypes = [HANDLE, USHORT, LONG, POINTER(UINT)]
        self.MoveWithVelocity.restype = BOOL

        self.ActivateProfileVelocityMode = self.rotationMotor.VCS_ActivateProfileVelocityMode
        self.ActivateProfileVelocityMode.argtypes = [HANDLE, USHORT, POINTER(UINT)]
        self.ActivateProfileVelocityMode.restype = BOOL

        self.HaltVelocityMovement = self.rotationMotor.VCS_HaltVelocityMovement
        self.HaltVelocityMovement.argtypes = [HANDLE, USHORT, POINTER(UINT)]
        self.HaltVelocityMovement.restype = BOOL

        #Position Mode
        self.ActivateProfilePositionMode = self.rotationMotor.VCS_ActivateProfilePositionMode
        self.ActivateProfilePositionMode.argtypes = [HANDLE, USHORT, POINTER(UINT)]
        self.ActivateProfilePositionMode.restype = BOOL

        self.SetPositionProfile = self.rotationMotor.VCS_SetPositionProfile
        self.SetPositionProfile.argtypes = [HANDLE, USHORT, UINT, UINT, UINT, POINTER(UINT)]
        self.SetPositionProfile.restype = BOOL

        self.MoveToPosition = self.rotationMotor.VCS_MoveToPosition
        self.MoveToPosition.argtypes = [HANDLE, USHORT, LONG, INT, INT, POINTER(UINT)]
        self.MoveToPosition.restype = BOOL

        self.HaltPositionMovement = self.rotationMotor.VCS_HaltPositionMovement
        self.HaltPositionMovement.argtypes = [HANDLE, USHORT, POINTER(UINT)]
        self.HaltPositionMovement.restype = BOOL
        
        #Max Speed
        self.SetMaxProfileVelocity = self.rotationMotor.VCS_SetMaxProfileVelocity
        self.SetMaxProfileVelocity.argtypes = [HANDLE, USHORT, UINT, POINTER(UINT)]
        self.SetMaxProfileVelocity.restype = BOOL

        #Motor Speed and Position Info
        self.GetPosition = self.rotationMotor.VCS_GetPositionIs
        self.GetPosition.argtypes = [HANDLE, USHORT, POINTER(INT), POINTER(UINT)]
        self.GetPosition.restype = BOOL

        self.GetVelocity = self.rotationMotor.VCS_GetVelocityIs
        self.GetVelocity.argtypes = [HANDLE, USHORT, POINTER(INT), POINTER(UINT)]
        self.GetVelocity.restype = BOOL

	# TO Do halt	

        #Close Device
        self.CloseDevice = self.rotationMotor.VCS_CloseDevice
        self.CloseDevice.argtypes = [HANDLE, POINTER(UINT)]
        self.CloseDevice.restype = BOOL

        #Close All Device
        self.CloseAllDevices = self.rotationMotor.VCS_CloseAllDevices
        self.CloseAllDevices.argtypes = [POINTER(UINT)]
        self.CloseAllDevices.restype = BOOL
            
        self.open_device()
       
    def print_usage(self):
        print "Usage: Maxon EPOS MVision Dev"
        print "node id (default 1)"
        print "device name (EPOS2, EPOS4, default - EPOS4)"
        print "protocol stack name (MAXON_RS232, CANopen, MAXON SERIAL V2, default - MAXON SERIAL v2)"
        print "interface name(RS232, USB, CAN_ixx_usb 0, CAN_kvaser_usb 0, ... default - USB)"
        print "port name (COM1, USB0, CAN0, ... default -USB0)"
        print "baudrate (115200, 1000000, ... default - 1000000)"
        print "list available interface (valid device name and protocol stack required)"
        print "list suppoerted protocol(valid device name required)"
        print "display device version"

    def print_setting(self):
        print "default setting"
        print "node id              =",self.RMNodeId
        print "device name          =",self.pDeviceName
        print "protocol stack name  =",self.pProtocolStackName
        print "interface name       =",self.pInterfaceName
        print "port name            =",self.pPortName
        print "baudrate             =",self.lBaudrate
    
    #def set_default_parameters(self):
        

    #Open Device
    def open_device(self):
        Result = 0
        oIsFault = BOOL(0)
        oIsEnabled = BOOL(0)

        print "Open Device-----"
        self.RMHandle = self.OpenDevice(self.pDeviceName, self.pProtocolStackName, self.pInterfaceName, self.pPortName, byref(self.errorCode))
        #self.RMHandle = OpenDevice(CHAR(2), CHAR("EPOS2"), CHAR("MAXON SERIAL V2"), CHAR("USB"), CHAR("USB0"), byref(self.errorCode))

        print self.RMHandle, self.errorCode.value
        if self.max_speed() == 0:
           return Result

        self.ClearFault(self.RMHandle, self.RMNodeId, byref(self.errorCode))
        self.SetEnableState(self.RMHandle, self.RMNodeId, byref(self.errorCode))
        
        #Set Max Speed

##        
##        if self.RMHandle != 0 and self.errorCode.value == 0:
##            if self.GetProtocolStackSettings(self.RMHandle, byref(self.lBaudrate), byref(self.lTimeout), byref(self.errorCode)) != BOOL(0):
##                if self.SetProtocolStackSettings(self.RMHandle, self.lBaudrate, self.lTimeout, byref(self.errorCode)) != BOOL(0):
##                    if self.GetProtocolStackSettings(self.RMHandle, byref(self.lBaudrate), byref(self.lTimeout), byref(self.errorCode)) != BOOL(0):
##                        Result = 1
##        else:
##            self.RMHandle = HANDLE(0)
##        if self.GetFaultState(self.RMHandle, self.RMNodeId, byref(oIsFault), byref(self.errorCode)) == BOOL(0):
##            Result = 0
##        if Result:
##            if oIsFault != BOOL(0):
##                if self.ClearFault(self.RMHandle, self.RMNodeId, byref(self.errorCode)) == BOOL(0):
##                    Result = 0
##            if self.GetEnableState(self.RMHandle, self.RMNodeId, byref(oIsEnabled), byref(self.errorCode)) == BOOL(0):
##                Result = 0
##            if oIsEnabled == BOOL(0):
##                if self.SetEnableState(self.RMHandle, self.RMNodeId, byref(self.errorCode)) == BOOL(0):
##                    Result = 0

        return Result       

    #Max Speed
    def max_speed(self):
        Result = 0
        if self.SetMaxProfileVelocity(self.RMHandle, self.RMNodeId, UINT(2000), byref(self.errorCode)) != BOOL(0):
            Result = 1
        return Result

    #Position Mode
    def rm_move_to_position(self, positionModeSpeed, targetRelativePosition):
        Result = 1
#        positionModeSpeed = UINT(20)
        positionModeAcceleration = UINT(1000)
        positionModeDeceleration = UINT(1000)

        #self.ActivateProfileVelocityMode(self.RMHandle, self.RMNodeId, byref(self.errorCode))

        #self.MoveWithVelocity(self.RMHandle, self.RMNodeId, LONG(TargetVelocity), byref(self.errorCode))
        #time.sleep(1)

        self.ActivateProfilePositionMode(self.RMHandle, self.RMNodeId, byref(self.errorCode))
        self.SetPositionProfile(self.RMHandle, self.RMNodeId, UINT(positionModeSpeed), positionModeAcceleration, positionModeDeceleration, byref(self.errorCode))
        self.MoveToPosition(self.RMHandle, self.RMNodeId, LONG(targetRelativePosition), INT(0), INT(1), byref(self.errorCode))
        
        #if self.ActivateProfilePositionMode(self.RMHandle, self.RMNodeId, byref(self.errorCode)) != 0:
            #if self.SetPositionProfile(self.RMHandle, self.RMNodeId, positionModeSpeed, positionModeAcceleration, positionModeDeceleration, byref(self.errorCode)) != 0:
                #print self.SetPositionProfile(self.RMHandle, self.RMNodeId, positionModeSpeed, positionModeAcceleration, positionModeDeceleration, byref(self.errorCode))
                #Result = 0
                #print self.MoveToPosition(self.RMHandle, self.RMNodeId, LONG(targetRelativePosition), INT(0), INT(1), byref(self.errorCode))
                #time.sleep(3)
                #if self.MoveToPosition(self.RMHandle, self.RMNodeId, LONG(targetRelativePosition), INT(0), INT(1), byref(self.errorCode)) == 0:
                    #Result = 0
        return Result

    #Halt Position Mode
    def rm_halt_position_mode(self):
        Result = 1
        if self.HaltPositionMovement(self.RMHandle, self.RMNodeId, byref(self.errorCode)) == BOOL(0):
            Result = 0
        return Result

    #Get Position and Speed Info
    def rm_speed_and_position(self):
        Result = 0
        if self.GetPosition(self.RMHandle, self.RMNodeId, byref(self.rmPosition), byref(self.errorCode)) != BOOL(0):
            if self.GetVelocity(self.RMHandle, self.RMNodeId, byref(self.rmVelosity), byref(self.errorCode)) != BOOL(0):
                Result = 1
        return Result

    #Close Device
    def close_device(self):
        Result = 0
        if self.CloseDevice(self.RMHandle, byref(self.errorCode)) != BOOL(0):
            Result = 1
        return Result


    def rm_move(self, TargetVelocity):
        Result = 1
#        positionModeSpeed = UINT(20)
        positionModeAcceleration = UINT(1000)
        positionModeDeceleration = UINT(1000)
        self.ActivateProfileVelocityMode(self.RMHandle, self.RMNodeId, byref(self.errorCode))

        self.MoveWithVelocity(self.RMHandle, self.RMNodeId, LONG(TargetVelocity), byref(self.errorCode))
       
	#if self.ActivateProfilePositionMode(self.RMHandle, self.RMNodeId, byref(self.errorCode)) != 0:
            #if self.SetPositionProfile(self.RMHandle, self.RMNodeId, positionModeSpeed, positionModeAcceleration, positionModeDeceleration, byref(self.errorCode)) != 0:
                #print self.SetPositionProfile(self.RMHandle, self.RMNodeId, positionModeSpeed, positionModeAcceleration, positionModeDeceleration, byref(self.errorCode))
                #Result = 0
		#print self.MoveToPosition(self.RMHandle, self.RMNodeId, LONG(targetRelativePosition), INT(0), INT(1), byref(self.errorCode)2
                #time.sleep(3)
                #if self.MoveToPosition(self.RMHandle, self.RMNodeId, LONG(targetRelativePosition), INT(0), INT(1), byref(self.errorCode)) == 0:
                    #Result = 0
        return Result        

##################################################################################################################################################################################

#test maxon motor to move on position mode
#guidewireRotateMotor = MaxonMotor(1, "EPOS2", "MAXON SERIAL V2", "USB", "USB1", 1000000)
#guidewireRotateMotor.rm_move_to_position(400,8000*50)
#time.sleep(60)
#guidewireRotateMotor.rm_halt_position_mode()



#guidewireRotateMotor2 = MaxonMotor(2, "EPOS2", "MAXON SERIAL V2", "USB", "USB0", 1000000)
#guidewireRotateMotor2.rm_move_to_position(200*10, -8000*40)
#guidewireRotateMotor2.rm_move(-int(1/TRANS_EFFICIENT));
#time.sleep(4)
#guidewireRotateMotor2.rm_move(0);
#guidewireRotateMotor.close_device()
#guidewireRotateMotor2.close_device()
