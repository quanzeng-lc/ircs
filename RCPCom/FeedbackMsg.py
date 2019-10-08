import RCPDatagram


class FeedbackMsg:
    def __init__(self):
        self.force_type = 0     #1
        self.force_direction = 0 # 1
        self.force_value = 0 # 2


    def get_force_type(self):
        return self.force_type

    def set_force_type(self, force_type):
        self.force_type = force_type

    def set_force_direction(self, force_direction):
        self.force_direction = force_direction

    def get_force_direction(self):
        return self.force_direction

    def get_force_value(self):
        return self.force_value

    def set_force_value(self, force_value):
        self.force_value = force_value


    def transform_datagram_into_feedback_msg(self, datagram):
        datagram_body = datagram.get_itc_datagram_body()
        self.force_type = ord(datagram_body[0])
        self.force_direction = ord(datagram_body[1])
        self.force_value = ord(datagram[2]) + ord(datagram_body[3])*256


