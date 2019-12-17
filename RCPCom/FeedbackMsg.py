import RCPCom.RCPDatagram

class FeedbackMsg:
    def __init__(self):
        # header 10 bytes
        self.force_direction = 0    #1
        self.force_value = 0    #2
        self.torque_direction = 0    #1
        self.torque_value = 0    #2

    def get_force_direction(self):
        return self.force_direction

    def set_force_direction(self, force_direction):
        self.force_direction = force_direction

    def get_force_value(self):
        return self.force_value

    def set_force_value(self, force_value):
        self.force_value = force_value

    def get_torque_direction(self):
        return self.torque_direction

    def set_torque_direction(self, torque_direction):
        self.torque_direction = torque_direction

    def get_torque_value(self):
        return self.torque_value

    def set_torque_value(self, torque_value):
        self.torque_value = torque_value

    def transform_datagram_into_feedback_msg(self, datagram):
        datagram_body = datagram.get_itc_datagram_body()
        self.force_direction = ord(datagram_body[0])
        self.force_value = ord(datagram_body[1]) + ord(datagram_body[2])*256
        self.torque_direction = ord(datagram_body[3])
        self.torque_value = ord(datagram_body[4]) + ord(datagram_body[5])*256
