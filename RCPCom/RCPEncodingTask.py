# -*- coding: utf-8 -*-
import io
import os
import socket
import struct
import mmap
import threading
import time
import FeedbackMsg
import sys
#sys.path.append("..")
import RCPControl.Feedback


class RCPEncodingTask:
    def __init__(self, context, output_queue_manager):
        self.context = context
        self.output_queue_manager = output_queue_manager
	self.flag = True
        self.encodingThread = threading.Thread(None, self.encodage)
	#self.encodingThread.start()

	
    def stop(self):
	self.flag = False

    def encodage(self):
        while self.flag:
            # send system status to incoming client
            if self.output_queue_manager.get_length() > 0:
                for cpt in range(0, self.output_queue_manager.get_length()):
                    if self.context.get_feedback_sequence_length()>0:
		        msg = self.context.fetch_latest_feedback_msg()
                        #context transform into datagram
                        msg = RCPDatagram()
                        msg.set_data_type(3)
                        msg.set_origine_id(5)
                        msg.get_target_id(4)
                        msg.set_time_stamps(123456)
                        msg.set_dlc(10)
                        msg_body += chr(0) + chr(direction) + chr(forcevalue % 256) + chr(forcevalue / 256)
                        msg.set_itc_datagram_body(msg_body)
		        self.output_queue_manager.add_datagram_by_id(cpt, msg)
            time.sleep(0.05)

