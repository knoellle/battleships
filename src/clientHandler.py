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
                    # prompt user with relevant information
                    self.sendBoards()
                    self.send(f"\nPlace ship of size {size}: ")
                    resp = self.receive(1024).strip()

                    # parse input
                    matches = ex.findall(resp)
                    if len(matches) == 0:
                        continue
                    matches = matches[0]
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

                    # check whether position is valid
                    blocked = False
                    for x in range(max(x0, 0), min(x0 + w, self.game.boardWidth)):
                        for y in range(max(y0, 0), min(y0 + h, self.game.boardHeight)):
                            if self.game.boards[self.playerNumber][y][x] == "o":
                                blocked = True
                                break
                        if blocked:
                            self.send("Invalid position, blocked by another ship")
                            break
                    if blocked:
                        self.game.unlock(self.playerNumber)
                        continue

                    # place ship
                    for x in range(x0, x0 + w):
                        for y in range(y0, y0 + h):
                            self.game.boards[self.playerNumber][y][x] = "o"

                    self.game.unlock(self.playerNumber)

                    break

        self.game.reportReady(self.playerNumber)
        self.send("Waiting for other player...")
        self.game.gameReady.wait()

        self.running = True
        while self.running:
            data = self.socket.recv(1024)
            self.socket.sendall(data)

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
