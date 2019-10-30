import socket
import threading
import re
import random
import time


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
        self.running = True

        # wait for all players to join the game
        self.send("Waiting for players to join...")
        self.game.gameReady.wait()
        self.send("Players found, game starting now")
        self.send(f"You are player {self.playerNumber}")

        # set up boards
        randomize = False
        for sizeIndex, num in enumerate(self.game.ships):
            size = sizeIndex + 1
            for _ in range(num):
                while self.running:
                    # prompt user with relevant information
                    self.sendBoards()

                    if randomize:
                        w, h = 1, 1
                        if random.random() > 0.5:
                            w = size
                        else:
                            h = size
                        x0 = random.randrange(self.game.boardWidth - w)
                        y0 = random.randrange(self.game.boardHeight - h)
                    else:
                        self.send(f"\nPlace ship of size {size}: ", suffix="")
                        resp = self.receive(1024)

                        if resp == "?" or resp == "help":
                            pass

                        if resp.startswith("r"):
                            randomize = True
                            continue

                        # parse input
                        w = 1
                        h = 1
                        if resp.endswith("-"):
                            w = size
                        else:
                            h = size

                        coords = self.cellToCoordinates(resp.strip("-"))
                        if coords is None:
                            self.send("Invalid coordinates!")
                            continue
                        y0, x0 = coords

                    if x0 + w > self.game.boardWidth:
                        self.send("X coordinate out of range")
                        continue
                    if y0 + h > self.game.boardHeight:
                        self.send("Y coordinate out of range")
                        continue

                    self.game.lock(self.playerNumber)

                    if not self.game.placeShip(y0, x0, h, w):
                        self.send("Invalid position, blocked by another ship")
                        self.game.unlock(self.playerNumber)
                        continue

                    self.game.unlock(self.playerNumber)

                    break

        # send final version of the board
        self.sendBoards()

        self.game.reportReady(self.playerNumber)
        self.send("Waiting for other player...")
        self.game.gameReady.wait()
        self.send("\n\nGame starting.")

        # continue playing until the game ends
        while self.running and self.game.result is None:
            print(f"{self.playerNumber} attempting lock")
            if self.game.lock(self.playerNumber):
                self.send("\nYour turn.")
                while True:
                    print(f"{self.playerNumber} get user input")
                    self.send("Choose a cell to fire at: ", suffix="")

                    resp = self.receive(1024)
                    coords = self.cellToCoordinates(resp)
                    if coords is None:
                        self.send("Invalid coordinates!")
                        continue
                    y, x = coords
                    result = self.game.fire(y, x)
                    if result == 0:
                        self.send("Miss!")
                    if result == 1:
                        self.send("Hit!")
                    if result == 2:
                        self.send("Hit and sunk!")
                    if result == 3:
                        self.send("\nYou won!\n")
                        self.game.unlock(self.playerNumber)
                        self.close()
                        return

                    self.sendBoards()
                    break

                self.game.turn = 1 - self.playerNumber
                self.game.unlock(self.playerNumber)
            else:
                print(f"{self.playerNumber} else case")
                print("sleeping")
                time.sleep(2)
                print("sleeping done")

        if self.game.result is not None:
            self.send("\nYou lost!\n")
            print("{self.playerNumber} lost")
            self.close()
            return

    def close(self):
        self.running = False
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
