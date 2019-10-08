import io
import socket
import threading
from IncomingClient import Client
import os
import threading as td
from RCPInputQueue import InputQueue


class TcpServer:
    def __init__(self, input_queue_manager, port):
        self.inputQueueManager = input_queue_manager
        self.port = port
        self.userNum = 0
        self.server_socket = None
        self.flag = True
        self.listeningTask = threading.Thread(None, self.listening)
        self.clientList = list()

    # socket use to listening
    def create_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(10)
        self.listeningTask.start()

    def terminate_server(self):
	print "socket server close"
        self.flag = False
        self.server_socket.close()

    def listening(self):
        while self.flag:
            print 'waiting for the client:', self.userNum
            connection, address = self.server_socket.accept()
            print 'incoming connection...', address

            input_queue = InputQueue()
            self.inputQueueManager.add_rcp_input_queue(input_queue)

#            print "inputQueueManager", self.inputQueueManager.get_length()

            client = Client(connection, address, self.userNum, self.inputQueueManager)
            client.enable()

            self.clientList.append(client)

            self.userNum += 1

    def set_current_state(self, current_state):
        for client in self.clientList:
            client.set_current_state(current_state)

    def launch(self):
        self.create_server()

    def close(self):
        self.flag = False
