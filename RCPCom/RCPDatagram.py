class RCPDatagram:
    def __init__(self, msg = None):
        # header 10 byte
        self.data_type = 0  # 2
        self.origin_id = 0  # 1
        self.target_id = 0  # 1
        self.timestamps = 123456 # 4
        self.dlc = 4  # 2

        # body
        self.body = ''
        if msg is not None:
            self.decode(msg)


    def get_data_type(self):
        return self.data_type
        
    def set_data_type(self, data_type):
        self.data_type = data_type
        
    def get_target_id(self):
        return self.target_id
    
    def set_target_id(self, target_id):
        self.target_id = target_id
        
    def get_origine_id(self):
        return self.origin_id
    
    def set_origine_id(self, origin_id):
        self.origin_id = origin_id

    def get_time_stamps(self):
        return self.timestamps
    
    def set_time_stamps(self, time_stampes):
        self.timestamps = time_stampes
    
    def get_dlc(self):
        return self.dlc
    
    def set_dlc(self, dlc):
        self.dlc = dlc

    def get_itc_datagram_body(self):
        return self.body

    def set_itc_datagram_body(self, body):
        self.body = body

    def decode(self, byte_array):
        self.data_type = ord(byte_array[0]) + ord(byte_array[1])*256  # 2
        self.origin_id = ord(byte_array[2])  # 1
        self.target_id = ord(byte_array[3])  # 1
        self.timestamps = ord(byte_array[4]) + ord(byte_array[5])*256 + ord(byte_array[6])*256*256 + ord(byte_array[7])*256*256*256  # 4
        self.dlc = ord(byte_array[8]) + ord(byte_array[9])*256  # 2
        self.body = byte_array[10:1024]
        
    def encode(self):
        timestamps_msb = self.timestamps/(2**16)
        timestamps_lsb = self.timestamps % (2**16)

        msg = chr(self.data_type % 256) + chr(self.data_type/256) \
              + chr(self.origin_id) + chr(self.target_id)\
              + chr(timestamps_lsb % 256) + chr(timestamps_lsb/256) \
              + chr(timestamps_msb % 256) + chr(timestamps_msb/256) \
              + chr(self.dlc % 256) + chr(self.dlc/256)
        msg += self.body
        msg_len = len(msg)

        for x in range(msg_len, 1024):
            msg += ' '
        return msg
