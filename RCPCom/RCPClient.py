# -*- coding: utf-8 -*-
import socket
import threading
import time
import os
from RCPOutputQueue import OutputQueue
from RCPCom.RCPOutputQueueManager import OutputQueueManager


class RCPClient:
    def __init__(self, _outputQueueManager):
        self.launching = False

        self.normal_frame_count = 0
        self.reconstruct_frame_count = 0

        self.clientSocket = None
        self.connection = None
	self.output_queue_manager = _outputQueueManager 
	self.output_queue = OutputQueue()
	self.output_queue_manager.add_rcp_output_queue(self.output_queue)
        self.rtTask = threading.Thread(None, self.execute_rt_task)
        self.msg_list = list()
        self.cpt = 0
        self.addr = ''

    def launch(self):
        self.launching = True
        self.rtTask.start()

    def get_addr(self):
        return self.addr

    def msg_producer(self):
	if self.output_queue_manager.get_length()>0:
	   if self.output_queue_manager.get_data_array_count_from_output_queue(0)>0:
	        msg = self.output_queue_manager.get_data_array_from_output_queue(0)
              	#print 'ultra sound:', msg
	        # self.msg_list.append(self.generate_msg(int(msg)))
		self.connection.sendall(msg.encode())
	      
        #time.sleep(0.1)

    def generate_msg(self, v):
	
        # header 10 byte
        data_type = 8  # 2
        origin_id = 0  # 1
        target_id = 0  # 1
        timestamps = 123456  # 4
        dlc = 4  # 2

        # body
        motor_type = 0  # 1
        symbol = 0  # 1
        speed = 120  # 2

        timestamps_msb = timestamps / (2 ** 16)
        timestamps_lsb = timestamps % (2 ** 16)
	
	value = int(v)	

	if value > 255:
		value = 255
	if value < 0:
		value = 0

        msg = chr(data_type % 256) + chr(data_type / 256) \
              + chr(origin_id) + chr(target_id) \
              + chr(timestamps_lsb % 256) + chr(timestamps_lsb / 256) \
              + chr(timestamps_msb % 256) + chr(timestamps_msb / 256) \
              + chr(dlc % 256) + chr(dlc / 256) + chr(value)
        msg_len = len(msg)
        for x in range(msg_len, 1024):
            msg += ' '

        self.cpt += 1

        return msg

    def send_handshake_message(self):
	print 'send handske message'        
        # header 10 byte
        data_type = 1  # 2
        origin_id = 1  # 1
        target_id = 0  # 1
        timestamps = 123456  # 4
        dlc = 6  # 2

        # body
        ip = [192, 168, 1, 156]  # 4
        port = 10704  # 2

        timestamps_msb = timestamps / (2 ** 16)
        timestamps_lsb = timestamps % (2 ** 16)

        msg = chr(data_type % 256) + chr(data_type / 256) \
              + chr(origin_id) + chr(target_id) \
              + chr(timestamps_lsb % 256) + chr(timestamps_lsb / 256) \
              + chr(timestamps_msb % 256) + chr(timestamps_msb / 256) \
              + chr(dlc % 256) + chr(dlc / 256) + chr(ip[0]) + chr(ip[1]) + chr(ip[2]) + chr(ip[3]) \
              + chr(port % 256) + chr(port / 256)
        print 'hand shake msg sending', data_type % 256, data_type / 256
        msg_len = len(msg)

        for x in range(msg_len, 1024):
            msg += ' '
        self.connection.sendall(msg)

    def connectera(self, addr, port):
        print "connect server", addr, port
        self.addr = addr
        self.connection = socket.socket()
        self.connection.connect((addr, port))
        #time.sleep(1)
	for i in range(3):
            self.send_handshake_message()

    def launch_trasmission_task(self):
        print "connected... start real time communication task"
        self.launching = True
        self.rtTask.start()

    def fermeture(self):
        self.connection.\
            close()

    def task(self):
        if len(self.msg_list) > 0:
            self.connection.sendall(self.msg_list.pop(0))

    def execute_rt_task(self):
        while self.launching:
            #print "executer"
            self.msg_producer()
            # self.task()
            time.sleep(0.1)
        self.fermeture()

    def read_all(self, count):
        buf = b''
        while count:
            receiving_buffer = self.clientSocket.recv(count)
            if not receiving_buffer:
                return None
            buf += receiving_buffer
            count -= len(receiving_buffer)
        return buf

    def transmit(self, file_path):

        if os.path.exists(file_path):
            img = self.do_parse_raw_file(file_path)
            self.connection.sendall(str(len(img)).ljust(16))
            self.connection.sendall(img)
            # time.sleep(0.02)
            os.remove(file_path)
            print file_path, "transmitted"
            return True
        else:
            img = self.do_parse_raw_file('./navi/default.raw')
            self.connection.sendall(str(len(img)).ljust(16))
            self.connection.sendall(img)
            # print "waiting for", image_a_envoye
            time.sleep(1)
            return False

    def do_parse_raw_file(self, path):
        f = open(path, "r+b")
        img = f.read()
        f.close()
        return img

    def status_check(self):
        type_len = self.read_all(16)

        if not type_len:
            print "error,unknow type file"

        self.system_status = self.read_all(int(type_len))
        # print "system status:", self.system_status
