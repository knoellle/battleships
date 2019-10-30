import socket
import threading

import game
import clientHandler


class BattleshipsServer():

    def __init__(self, host="", port=9999):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen()
        self.connections = []

    def run(self):
        self.running = True
        # accept connections until the server is terminated
        g = game.Game()
        while self.running:
            try:
                sock, address = self.socket.accept()
                print("Player connected from", address)
                player = clientHandler.ClientHandler(sock, self, g)
                player.start()
                self.connections.append(player)
                if g.gameReady.is_set():
                    # game is full, set up a new one
                    g = game.Game()
            except Exception as e:
                # disconnect existing players
                for thread in self.connections:
                    thread.close()
                    thread.join()

                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()

                self.running = False
                raise e


def main():
    server = BattleshipsServer()
    server.run()


if __name__ == "__main__":
    main()
