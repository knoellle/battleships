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
        return self.socket.sendall((string + suffix).encode())

    def receive(self, maxBytes, strip=True):
        s = self.socket.recv(maxBytes).decode()
        if strip:
            s = s.strip()
        return s

    def sendBoards(self):
        rownames = "ABCDEFGHIJ"
        s = ""
        self.game.lock(self.playerNumber)
        ownBoard = self.game.renderBoard(self.playerNumber)
        otherBoard = self.game.renderBoard(1 - self.playerNumber)
        self.game.unlock(self.playerNumber)
        colnames = " ".join(map(str, range(0, 10)))
        s += "  " + colnames + "      " + colnames + "\n"
        for i in range(len(ownBoard)):
            s += f"{rownames[i]} {ownBoard[i]}    {rownames[i]} {otherBoard[i]}\n"
        self.send(s)

    def cellToCoordinates(self, cell):
        ex = re.compile(r"([a-jA-J])(\d)")
        matches = ex.findall(cell)
        if len(matches) == 0:
            return None
        matches = matches[0]
        if len(matches[0]) != 1 or not matches[1].isdigit():
            return None
        y = ord(matches[0].lower()) - ord("a")
        x = int(matches[1])
        return y, x

    def run(self):
        # wait for all players to join the game
        self.send("Waiting for players to join...")
        self.game.gameReady.wait()
        self.send("Players found, game starting now")
        self.send(f"You are player {self.playerNumber}")

        # set up boards
        for sizeIndex, num in enumerate(self.game.ships):
            size = sizeIndex + 1
            for i in range(num):
                while True:
                    # prompt user with relevant information
                    self.sendBoards()
                    self.send(f"\nPlace ship of size {size}: ", suffix="")
                    resp = self.receive(1024).strip()

                    if resp == "?" or resp == "help":
                        pass

                    # parse input
                    coords = self.cellToCoordinates(resp.strip("-"))
                    if coords is None:
                        self.send("Invalid coordinates!")
                        continue
                    y0, x0 = coords

                    w = 1
                    h = 1
                    if resp.endswith("-"):
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
                    for x in range(max(x0-1, 0), min(x0 + w + 1, self.game.boardWidth)):
                        for y in range(max(y0-1, 0), min(y0 + h + 1, self.game.boardHeight)):
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

        # send final version of the board
        self.sendBoards()

        self.game.reportReady(self.playerNumber)
        self.send("Waiting for other player...")
        self.game.gameReady.wait()
        self.send("\n\nGame starting.")

        while True:
            if self.game.turn == self.playerNumber:
                self.game.lock()
                self.send("\nYour turn.")
                while True:
                    self.send("Choose a cell to fire at: ", suffix="")

                    resp = self.socket.recv(1024)
                    coords = self.cellToCoordinates(resp)
                    if coords is None:
                        self.send("Invalid coordinates!")
                        continue
                    y, x = coords
                    result = game.fire(y, x)
                    if result = 0:
                        self.send("Miss!")
                    if result = 1:
                        self.send("Hit!")
                    if result = 2:
                        self.send("Hit and sunk!")
                self.socket.sendall(data)

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
