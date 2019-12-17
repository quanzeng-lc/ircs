from RCPCom.TcpServer import TcpServer
import threading

class OutputQueue():
    def __init__(self):
        self.outputQueueLock = threading.Lock()
        self.outputQueue = []

    def append(self, datagram):
        self.outputQueue.append(datagram)

    def get_latest_array(self):
        self.outputQueueLock.acquire()
        if len(self.outputQueue) > 0:
            ret = self.outputQueue.pop(0)
        self.outputQueueLock.release()
        return ret

    def get_length(self):
        self.outputQueueLock.acquire()
        length = len(self.outputQueue)
        self.outputQueueLock.release()
        return length
