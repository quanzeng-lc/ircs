import serial
import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import struct
import thread
import time

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

        # Connect to the slave
#        master = modbus_rtu.RtuMaster(
#            serial.Serial(port=PORT, baudrate=9600, bytesize=8, parity='N', stopbits=1, xonxoff=0)
#        )
        self.master = modbus_rtu.RtuMaster(
                serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, parity=self.parity, stopbits=self.stopbits, xonxoff=0)
                )
        self.master.set_timeout(4)
        self.master.set_verbose(True)


    def aquireForce(self):
        output = self.master.execute(1, cst.READ_HOLDING_REGISTERS, 30, 2)
        bb = struct.unpack('>i', struct.pack('>HH', output[0], output[1]))
        out = bb[0]
#        print "output:", out
        return out           
