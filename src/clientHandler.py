import socket
import threading


class ClientHandler(threading.Thread):

    def __init__(self, socket, server, game):
        super().__init__()
        self.socket = socket
        self.server = server
        self.running = False
        self.game = game
        self.playerNumber = None
        self.game.addPlayer(self)

    def send(self, string):
        self.socket.sendall(string.encode())

    def sendBoards(self):
        s = ""
        self.game.lock(self.playerNumber)
        ownBoard = self.game.renderBoard(self.playerNumber)
        otherBoard = self.game.renderBoard(1 - self.playerNumber)
        self.game.unlock(self.playerNumber)
        for i in range(len(ownBoard)):
            s += f"{i} {ownBoard[i]}   {i} {otherBoard[i]}\n"
        self.send(s.encode())

    def run(self):
        # wait for all players to join the game
        self.send("Waiting for players to join...\n")
        self.game.gameReady.wait()
        self.send("Players found, game starting now\n")
        self.send(f"You are player {self.playerNumber}\n")

        self.sendBoards()

        self.running = True
        while self.running:
            data = self.socket.recv(1024)
            self.socket.sendall(data)

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
