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

    def sendBoards(self):
        s = ""
        self.game.lock(self.playerNumber)
        ownBoard = self.game.renderBoard(self.playerNumber)
        otherBoard = self.game.renderBoard(1 - self.playerNumber)
        self.game.unlock(self.playerNumber)
        for i in range(len(ownBoard)):
            s += f"{i} {ownBoard[i]}   {i} {otherBoard[i]}\n"
        self.socket.sendall(s.encode())

    def run(self):
        # wait for all players to join the game
        self.socket.sendall(b"Waiting for players to join...\n")
        self.game.gameReady.wait()
        self.socket.sendall(b"Players found, game starting now\n")
        self.socket.sendall(f"You are player {self.playerNumber}\n".encode())

        self.sendBoards()

        self.running = True
        while self.running:
            data = self.socket.recv(1024)
            self.socket.sendall(data)

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
