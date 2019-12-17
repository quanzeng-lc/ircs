import RCPCom.RCPDatagram


class MotorMsg:
    def __init__(self, msg):
        # header 10 byte
        self.motor_type = 0  # 1
        self.motor_orientation = 0  # 1
        self.motor_speed = 0  # 2
        self.motor_position = 0 # 2
        self.transform_datagram_into_motor_msg(msg)

    def get_motor_type(self):
        return self.motor_type
        
    def set_motor_type(self, motor_type):
        self.motor_type = motor_type
        
    def get_motor_orientation(self):
        return self.motor_orientation
    
    def set_motor_orientation(self, motor_orientation):
        self.motor_orientation = motor_orientation
        
    def get_motor_speed(self):
        return self.motor_speed
    
    def set_motor_speed(self, motor_speed):
        self.motor_speed = motor_speed

    def get_motor_position(self):
        return self.motor_position
    
    def set_motor_position(self, motor_position):
        self.motor_position = motor_position
    
    def transform_datagram_into_motor_msg(self, datagram):
        datagram_body = datagram.get_itc_datagram_body()
        self.motor_type = ord(datagram_body[0])
        self.motor_orientation = ord(datagram_body[1])
        self.motor_speed = ord(datagram_body[2]) + ord(datagram_body[3])*256
        self.motor_position = ord(datagram_body[4]) + ord(datagram_body[5])*256
