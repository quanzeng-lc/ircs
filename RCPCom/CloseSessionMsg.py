import RCPDatagram


class CloseSessionMessage:
    def __init__(self, msg):
        # header 10 byte
        self.hehe=0

        #self.transform_datagram_into_injection_msg(msg)
    """
    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume

    def get_speed(self):
        return self.speed

    def set_speed(self, speed):
        self.speed = speed

    def transform_datagram_into_injection_msg(self, datagram):
        datagram_body = datagram.get_itc_datagram_body()
        v =ord(datagram_body[0]) + ord(datagram_body[1])*256
        s = ord(datagram_body[2]) + ord(datagram_body[3])*256
        self.volume = v/100 + v%100*0.01
        self.speed = s/100 + s%100*0.01
    """"
