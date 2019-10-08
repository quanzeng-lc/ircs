# -*- coding: utf-8 -*-
import threading
import time


class RCPDecodingTask:
    def __init__(self, input_queue_manager, _context, _datagram_analyser):
        self.inputQueueManager = input_queue_manager
        self.context = _context
        self.datagramAnalyser = _datagram_analyser
	self.flag = True
        self.receptionTask = threading.Thread(None, self.decodage)
        self.receptionTask.start()
    
    def stop(self):
	self.flag = False

    def decodage(self):
        while self.flag:
            # send system status to incoming client
            if self.inputQueueManager.get_length() > 0:
                for cpt in range(0, self.inputQueueManager.get_length()):
                    if self.inputQueueManager.get_data_array_count_from_input_queue(cpt) > 0:
                        ret = self.inputQueueManager.get_data_array_from_input_queue(cpt)
                        self.datagramAnalyser.analyse(cpt, ret)

            time.sleep(0.02)
