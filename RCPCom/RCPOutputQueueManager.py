import threading


class OutputQueueManager():
    def __init__(self):
        self.rcpOutputQueueManager = list()
        self.rcpOutputQueueManagerLock = threading.Lock()
    
    def add_rcp_output_queue(self, output_queue):
	self.rcpOutputQueueManagerLock.acquire()
        self.rcpOutputQueueManager.append(output_queue)
	self.rcpOutputQueueManagerLock.release()

    def add_datagram_by_id(self, id, datagram):
	self.rcpOutputQueueManagerLock.acquire()
        self.rcpOutputQueueManager[id].append(datagram)
	self.rcpOutputQueueManagerLock.release()

    def get_length(self):
        self.rcpOutputQueueManagerLock.acquire()
        ret = len(self.rcpOutputQueueManager)
        self.rcpOutputQueueManagerLock.release()
        return ret

    def get_data_array_count_from_output_queue(self, cpt):
        self.rcpOutputQueueManagerLock.acquire()
        ret = self.rcpOutputQueueManager[cpt].get_length()
        self.rcpOutputQueueManagerLock.release()
        return ret

    def get_data_array_from_output_queue(self, cpt):
        self.rcpOutputQueueManagerLock.acquire()
        ret = self.rcpOutputQueueManager[cpt].get_latest_array()
        self.rcpOutputQueueManagerLock.release()
        return ret
