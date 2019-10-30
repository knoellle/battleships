import threading


class Game():

    def __init__(self):
        self._lock = threading._RLock()
        self.boardWidth = 10
        self.boardHeight = 10
        self.boards = [[[" " for _ in range(self.boardWidth)] for _ in range(
            self.boardHeight)] for _ in range(2)]  # two 10x10 boards
        self.numShipcells = [0, 0]
        self.players = []
        self.activePlayer = None
        self.turn = None
        self.gameReady = threading.Event()
        self.ships = [0, 1, 2, 1, 1]
        self.playersReady = 0
        self.result = None

    def renderBoard(self, player):

        def filterShips(c):
            if c == "o":
                return " "
            return c

        if player != self.activePlayer:
            board = [" ".join(map(filterShips, line)) for line in self.boards[player]]
        else:
            board = [" ".join(line) for line in self.boards[player]]
        return board

    def addPlayer(self, player):
        self.players.append(player)
        if len(self.players) == 2:
            print("players found")
            for i, p in enumerate(self.players):
                print(f"assigning player number {i} to {p}")
                p.playerNumber = i
            self.gameReady.set()

    def placeShip(self, y0, x0, h, w):
        # check whether position is valid
        for x in range(max(x0-1, 0), min(x0 + w + 1, self.boardWidth)):
            for y in range(max(y0-1, 0), min(y0 + h + 1, self.boardHeight)):
                if self.boards[self.activePlayer][y][x] == "o":
                    return False

        # place ship
        for x in range(x0, x0 + w):
            for y in range(y0, y0 + h):
                self.boards[self.activePlayer][y][x] = "o"
                self.numShipcells[self.activePlayer] += 1
        return True

    def reportReady(self, player):
        self.playersReady += 1
        self.gameReady.clear()
        if self.playersReady == 2:
            self.turn = 0
            self.gameReady.set()

    def findUnhitShip(self, y, x, dy, dx):
        while True:
            x += dx
            y += dy
            c = self.boards[1-self.activePlayer][y][x]
            if c == " ":
                return False
            if c == "o":
                return True

    def fire(self, y, x):
        # check whether a ship was hit
        if self.boards[1-self.activePlayer][y][x] == "o":
            # mark location
            self.boards[1-self.activePlayer][y][x] = "x"

            # decrease counter towards win condition
            self.numShipcells[1-self.activePlayer] -= 1
            if self.numShipcells[1-self.activePlayer] == 0:
                # all ships sunk
                self.turn = None
                self.result = self.activePlayer
                return 3

            # determine whether the ship was sunk
            if self.findUnhitShip(y, x, -1, 0) or self.findUnhitShip(y, x, 1, 0) \
                    or self.findUnhitShip(y, x, 0, -1) or self.findUnhitShip(y, x, 0, 1):
                # hit
                return 1
            else:
                # hit and sunk
                return 2
        elif self.boards[1-self.activePlayer][y][x] == "x":
            return 1
        else:
            self.boards[1-self.activePlayer][y][x] = "~"
            # miss
            return 0

    def lock(self, player):
        if self.turn is None:
            self._lock.acquire()
            self.activePlayer = player
            return True
        if self.turn == player:
            self._lock.acquire()
            self.activePlayer = player
            return True
        return False

    def unlock(self, player):
        if not self.activePlayer == player:
            raise Exception("Inactive player tried to release lock")
        self._lock.release()
        if self._lock._count == 0:
            self.activePlayer = None
