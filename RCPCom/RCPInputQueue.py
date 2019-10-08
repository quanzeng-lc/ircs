import threading


class InputQueue:
    def __init__(self):
        self.inputQueueLock = threading.Lock()
        self.inputQueue = list()

    def append(self, datagram):
        self.inputQueue.append(datagram)
        
    def get_latest_array(self):
        self.inputQueueLock.acquire()
        if len(self.inputQueue) > 0:
            ret = self.inputQueue.pop(0)
        self.inputQueueLock.release()
        return ret
        
    def get_length(self):
        self.inputQueueLock.acquire()
        length = len(self.inputQueue)
        self.inputQueueLock.release()
        return length
