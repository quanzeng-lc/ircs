from RCPCom.TcpServer import TcpServer
from RCPCom.RCPClient import RCPClient
import threading


class InputQueueManager():
    def __init__(self):
        self.rcpInputQueueManager = list()
        self.rcpInputQueueManagerLock = threading.Lock()

    def add_rcp_input_queue(self, input_queue):
        self.rcpInputQueueManager.append(input_queue)

    def add_datagram_by_id(self, id, datagram):
        self.rcpInputQueueManager[id].append(datagram)

    def get_length(self):
        self.rcpInputQueueManagerLock.acquire()
        ret = len(self.rcpInputQueueManager)
        self.rcpInputQueueManagerLock.release()
        return ret

    def get_data_array_count_from_input_queue(self, cpt):
        self.rcpInputQueueManagerLock.acquire()
        ret = self.rcpInputQueueManager[cpt].get_length()
        self.rcpInputQueueManagerLock.release()
        return ret

    def get_data_array_from_input_queue(self, cpt):
        self.rcpInputQueueManagerLock.acquire()
        ret = self.rcpInputQueueManager[cpt].get_latest_array()
        self.rcpInputQueueManagerLock.release()
        return ret
