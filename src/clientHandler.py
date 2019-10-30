import socket
import threading


class ClientHandler(threading.Thread):

    def __init__(self, socket, server):
        super().__init__()
        self.socket = socket
        self.server = server
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            data = self.socket.recv(1024)
            self.socket.sendall(data)

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
