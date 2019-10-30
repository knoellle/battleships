import socket
import threading
import re


class ClientHandler(threading.Thread):

    def __init__(self, socket, server, game):
        super().__init__()
        self.socket = socket
        self.server = server
        self.running = False
        self.game = game
        self.playerNumber = None
        self.game.addPlayer(self)

    def send(self, string, suffix="\n"):
        return self.socket.sendall(string.encode())

    def receive(self, maxBytes, strip=True):
        s = self.socket.recv(maxBytes).decode()
        if strip:
            s = s.strip()
        return s

    def sendBoards(self):
        s = ""
        self.game.lock(self.playerNumber)
        ownBoard = self.game.renderBoard(self.playerNumber)
        otherBoard = self.game.renderBoard(1 - self.playerNumber)
        self.game.unlock(self.playerNumber)
        for i in range(len(ownBoard)):
            s += f"{i} {ownBoard[i]}   {i} {otherBoard[i]}\n"
        self.send(s)

    def run(self):
        # wait for all players to join the game
        self.send("Waiting for players to join...")
        self.game.gameReady.wait()
        self.send("Players found, game starting now")
        self.send(f"You are player {self.playerNumber}")

        # set up boards
        ex = re.compile(r"([a-jA-J])(\d\d?)(-?)")
        for sizeIndex, num in enumerate(self.game.ships):
            size = sizeIndex + 1
            for i in range(num):
                while True:
                    self.sendBoards()
                    self.send(f"\nPlace ship of size {size}: ")
                    resp = self.receive(1024).strip()
                    matches = ex.findall(resp)[0]
                    print(matches)
                    if len(matches[0]) != 1 or not matches[1].isdigit():
                        self.send("Invalid input!")
                        continue
                    y0 = ord(matches[0].lower()) - ord("a")
                    x0 = int(matches[1])
                    w = 1
                    h = 1
                    if matches[2] == "-":
                        w = size
                    else:
                        h = size
                    if x0 + w > self.game.boardWidth:
                        self.send("X coordinate out of range")
                        continue
                    if y0 + h > self.game.boardHeight:
                        self.send("Y coordinate out of range")
                        continue
                    self.game.lock(self.playerNumber)
                    print(x0, y0, w, h)
                    for x in range(x0, x0 + w):
                        for y in range(y0, y0 + h):
                            self.game.boards[self.playerNumber][y][x] = "o"
                            print(f"setting {x}, {y}")
                    self.game.unlock(self.playerNumber)
                    print(self.game.boards)
                    break


        self.running = True
        while self.running:
            data = self.socket.recv(1024)
            self.socket.sendall(data)

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
