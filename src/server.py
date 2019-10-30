import socket

class BattleshipsServer():

    def __init__(self, host="", port=9999):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()

    def run(self):
        self.running = True
        while self.running:
            connection, address = self.socket.accept()
            print("Player connected from", address)

def main():
    server = BattleshipsServer()
    server.run()

