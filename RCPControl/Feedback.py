import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import struct
import threading
import time
import sys
from RCPContext.RCPContext import RCPContext

# PORT = 1 
#PORT = "/dev/ttyUSB0"

class Feedback(object):
    
    def __init__(self, port, baudrate, bytesize, parity, stopbits, context):
        #serial parameter set
        self.PORT = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.forceFeedback  = 0
        self.feedbackID = 0
        self.context = context
        lockFeedback = threading.Lock()
        #logger = modbus_tk.utils.create_logger("console")
        try:
            self.master = modbus_rtu.RtuMaster(
                serial.Serial(port=self.PORT, baudrate=self.baudrate, bytesize=self.bytesize, parity=self.parity, stopbits=self.stopbits, xonxoff=0)
                )
            self.master.set_timeout(4)
            self.master.set_verbose(True)
            #logger.info("connected")
        except modbus_tk.modbus.ModbusError as exc:
            #logger.error("%s- Code=%d", exc, exc.get_exception_code())
            print("error")
        self.feedbackTask = threading.Thread(None, self.aquireForce)  

    def aquireForce(self):
        while True:
            output = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 30, 2)
            bb = struct.unpack('>i', struct.pack('>HH', output[0], output[1]))
            out = bb[0]
    #        print "output:", out
            lockFeedback.acquire()
            self.forceFeedback = out
            if self.feedbackID is FeedbackType.FORCEFEEDBACK:
                self.context.setGlobalForceFeedback(out)
            elif self.feedbackID is FeedbackType.TORQUEFEEDBACK:
                self.context.setGlobalTorqueFeedback(out)
            self.context.setGlobal
            lockFeedabck.release()
            time.sleep(50)

    def obtainForce(self):
        acquireFeedback.acquire()
        ret =  self.forceFeedback
        acquireFeedback.release()
        return ret

    def setID(self, ID):
        self.feedbackID = ID

    def start(self):
        self.feedbackTask.start()

'''
forcePORT = "/dev/ttyUSB1"
torquePORT = "/dev/ttyUSB3"
baudrate = 9600
bytesize = 8
parity = 'N'
stopbits = 1
forcefeedback = Feedback(forcePORT, baudrate, bytesize, parity, stopbits)
torquefeedback = Feedback(torquePORT, baudrate, bytesize, parity, stopbits)
while True:
    forcevalue = forcefeedback.aquireForce()
    torquevalue = torquefeedback.aquireForce()
    time.sleep(0.01)
    print("force", forcevalue, "torque", torquevalue)
'''
