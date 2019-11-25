import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import struct
import threading
import time
import sys

# PORT = 1 
#PORT = "/dev/ttyUSB0"

class Feedback(object):
    
    def __init__(self, port, baudrate, bytesize, parity, stopbits):
        #serial parameter set
        self.PORT = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.forceFeedback  = 0
        self.hapticFeedbackID = 0
        self.lockFeedback = threading.Lock()
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
            self.lockFeedback.acquire()
            self.forceFeedback = out
            self.lockFeedback.release()
            time.sleep(0.01)

    def obtainForce(self):
        ret =  self.forceFeedback
        return ret

    def setID(self, ID):
        self.hapticFeedbackID = ID

    def start(self):
        self.feedbackTask.start()

forcePORT = "/dev/ttyUSB3"
baudrate = 9600
bytesize = 8
parity = 'N'
stopbits = 1
forcefeedback = Feedback(forcePORT, baudrate, bytesize, parity, stopbits)
forcefeedback.start()
while True:
    forcevalue = forcefeedback.obtainForce()
    time.sleep(0.1)
    print("force", forcevalue)

