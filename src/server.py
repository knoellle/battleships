import socket

import clientHandler


class BattleshipsServer():

    def __init__(self, host="", port=9999):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()
        self.connections = []

    def run(self):
        self.running = True
        # accept connections until the server is terminated
        while self.running:
            try:
                sock, address = self.socket.accept()
                print("Player connected from", address)
                thread = clientHandler.ClientHandler(sock, self)
                thread.start()
                self.connections.append(thread)
            except KeyboardInterrupt:
                self.running = False
                break

        # disconnect existing players
        for thread in self.connections:
            thread.close()
            thread.join()

        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()


def main():
    server = BattleshipsServer()
    server.run()


if __name__ == "__main__":
    main()
