# -*- coding: utf-8 -*-
import io
import os
import socket
import struct
import mmap
import threading
import time
from RCPCom.RCPDatagram import RCPDatagram 

class RCPEncodingTask:
    def __init__(self, context, output_queue_manager):
        self.context = context
        self.output_queue_manager = output_queue_manager
        self.flag = True
        self.encodingThread = threading.Thread(None, self.decodage)
        self.encodingThread.start()
	
    def stop(self):
        self.flag = False

    def decodage(self):
        while self.flag:
            # send system status to incoming client
            if self.output_queue_manager.get_length() > 0:
                for cpt in range(0, self.output_queue_manager.get_length()):
                    if self.context.get_feedback_sequence_length()>0:
                        msg = self.context.fetch_latest_feedback_msg()

                        forcedirection = msg.get_force_direction()
                        forcevalue = msg.get_force_value()
                        torquedirection = msg.get_torque_direction()
                        torquevalue = msg.get_torque_value()
                        datagram_body = chr(forcedirection) + chr(forcevalue%256) + chr(forcevalue / 256) + chr(torquedirection) + chr(torquevalue%256) + chr(torquevalue / 256)
                        
                        datagram = RCPDatagram()
                        datagram.set_data_type(6)
                        datagram.set_target_id(1)
                        datagram.set_origine_id(1)
                        datagram.set_time_stamps(12345)
                        datagram.set_dlc(10)
                        datagram.set_itc_datagram_body(datagram_body)
                        self.output_queue_manager.add_datagram_by_id(cpt, datagram)
            time.sleep(0.05)

