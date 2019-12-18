# Game-On-Python-Network

## Name of the game: Three sells and a pea

This is a game to emulate what it is like to play the street game where you guess which cup the ball is under.

## Requirements

- Python 3.75 advanced install
    - Check these boxes: pip and python environment variables installed
- Python Arcade


## How to run:

First install Python Arcade Api using “pip” via the command line in administrator mode by inputting “pip install arcade” into the command line. Then, you need to find the server and client in your finder. Then you need to open the server and specify what IP address the clients should be connecting to. Once that is done, start up at least two clients and have them connect to the servers IPv-4 address.
>Note: This only works with firewall disabled.

Have one of the clients start a a game. The client not hosting a game should be able to then click on "List games" and find the number of the game that they want to join. With that number they will navigate to the join games page and type in the number of the game they would like to join. Then you're in! You and your friend now have a peer-to-peer connection hosted on a server and are able to play the game. Enjoy!