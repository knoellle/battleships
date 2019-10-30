# Battleships Game Server
A socket based server that allows players to connect via telnet to play a game of [battleships](https://en.wikipedia.org/wiki/Battleships_(game)). This project is loosely based on a university course project where students were supposed to create a Tic Tac Toe game server. 

# User guide
After starting the `server.py` in your favorite python(3) environment, simply connect to your machine's IP at port 9999 (using telnet for example).
Once a second connection is established, the board setup phase begins and the players can place their ships.

## Board Setup Phase 
During this phase, ships can be placed by specifying the coordinate of the upper left corner of a ship, followed by a `-` to align it horizontally.

Examples:
```
A5   places the ship vertically the top center
A0-  places the ship horizontally in the upper left corner
r    places all the remaining ships randomly (may result in an infinite loop if there are too many ships to place. Feel free to PR a fix)
```

## Game Phase
The first player to connect to the server gets to play the first turn.
During a turn, a player can specify a set of coordinates to fire at in the same format as during the setup phase (without the orientation). Refer to the wikipedia site linked at the top for gameplay rules.
Once the game is over, one player receives a "You won!" message, while the other one receives a "You lost!". Following this, the server terminates the connection.

## Requirements
This project uses no external libraries and should work with any python 3.X version.
