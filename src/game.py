import threading


class Game():

    def __init__(self):
        self._lock = threading.Lock()
        self.boardWidth = 10
        self.boardHeight = 10
        self.boards = [[[" " for _ in range(self.boardWidth)] for _ in range(self.boardHeight)] for _ in range(2)]  # two 10x10 boards
        self.players = []
        self.activePlayer = None
        self.turn = None
        self.gameReady = threading.Event()
        self.ships = [0,1,2,1,1]

    def renderBoard(self, player):

        def filterShips(c):
            if c == "o":
                return " "
            return c

        board = ["".join(line) for line in self.boards[player]]
        if player != self.activePlayer:
            board = ["".join(map(filterShips, line)) for line in board]
        return board


    def addPlayer(self, player):
        self.players.append(player)
        if len(self.players) == 2:
            print("players found")
            for i, p in enumerate(self.players):
                print(f"assigning player number {i} to {p}")
                p.playerNumber = i
            self.gameReady.set()

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
        self.activePlayer = None
