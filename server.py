#####################################################################
# Game Server
# Developed by Alex van Zuiden-Rylander, Eyas Rashid and Leighlyn Ha
# Fall Quarter 2019
#####################################################################

import socket
import sys
import threading
import queue
import select
from collections import namedtuple

nextNum = 0  # keeps track of next game number to assign to game

# holds player name, Player objects used to keep track of players
Player = namedtuple('Player', 'name')

# Game holds information of open game for another player to join
# playerName = name of player creating game
# gameNumber = uniquely identifies game
# address = IP address of player creating game
Game = namedtuple('Game', 'playerName gameNumber address')

# returns a unique number to identify a game
def getGameNumber():
    global nextNum
    nextNum = nextNum + 1
    return nextNum

# registers player on server, returns Player object
def register(connection):
    global playerList
    try:
        # get player name
        playerName = ''
        char = connection.recv(1).decode('utf-8')
        while char != '\r':
            playerName += char
            char = connection.recv(1).decode('utf-8')
        # create player object and add it to list of players
        newPlayer = Player(playerName)
        playerList.append(newPlayer)
        print('added player: ' + playerName)
        return newPlayer
    except socket.error:
        print('Lost connection with player. Could not register player.')
    return None

# unregisters given Player object from server
def unregister(newPlayer):
    global playerList
    print('removing player: ' + getattr(newPlayer, 'name'))
    if (newPlayer is not None):
        playerList.remove(newPlayer)

# sends list of available games on server to client
def listGames(connection):
    global gameList
    # get list of available games
    gamesMsg = ''
    for game in range(len(gameList)):
        gamesMsg +='Game: ' + str(getattr(gameList[game], 'gameNumber')) + ', Player: ' + getattr(gameList[game], 'playerName') + '\n'
    # if no games available, send -1 to indicate no available games
    if (gamesMsg == ''):
        gamesMsg = '-1'
    gamesMsg += '\r'
    try:
        connection.send(gamesMsg.encode())
    except socket.error:
        print('Lost connection with player. Could not send list of games.')

# create new game for given Player object
# returns the newly created Game object
def createGame(connection, curPlayer, address):
    global gameList
    newGame = None
    try:
        if (curPlayer is None):
            return None
        # create new Game object with player's name, unique ID number, and player's IP address
        newGame = Game(getattr(curPlayer, 'name'), getGameNumber(), address[0])    
        gameList.append(newGame)
        # send game number to client
        curGameNum = str(getattr(newGame, 'gameNumber')) + '\r'
        connection.send(curGameNum.encode())
        print('created game: ' + str(getattr(newGame, 'gameNumber')))
    except socket.error:
        print('Lost connection with player: ' + str(getattr(curPlayer, 'name')) + '\nCould not create game.')
        if (newGame is not None):
            removeGame(newGame)
    return newGame

# remove game from list of games
def removeGame(curGame):
    global gameList
    global nextNum
    print('removing game: ' + str(getattr(curGame, 'gameNumber')))
    # remove given game from game list
    if (curGame is not None):
        gameList.remove(curGame)
    # if no games in list, reset game numbers to start from 1
    if (len(gameList) == 0):
        nextNum = 0

# allows player to join existing game
def joinGame(connection, curGame):
    global gameList    
    # read game number player wants to join
    try:
        gameNumber = ''
        char = connection.recv(1).decode('utf-8')
        while char != '\r':
            gameNumber += char
            char = connection.recv(1).decode('utf-8')    
        gameAddr = ''
        # if game number exists, send the other player's IP address
        for game in range(len(gameList)):
            if (str(getattr(gameList[game], 'gameNumber')) == gameNumber):
                gameAddr = str(getattr(gameList[game], 'address'))
                break
        # if game number does not exist, send -1 to notify player
        if (gameAddr == ''):
            gameAddr = '-1'
        gameAddr += '\r'
        connection.send(gameAddr.encode())
    except socket.error:
        print('Lost connection with player. Could not join player to game.')

# handles client requests for listing, creating, and joining games
def getClientInput(connection, curPlayer, address):
    option = ''
    curGame = None
    try:
        while option != '0':  # while client has not left server
            option = connection.recv(1).decode('utf-8')
            if (option == '1'):  # list available games
                listGames(connection)
            elif (option == '2'):  # create a game
                curGame = createGame(connection, curPlayer, address)
            elif (option == '3'):  # join a game
                joinGame(connection, curGame)
            elif (option == '4'):  # remove a game
                if (curGame is not None):
                    removeGame(curGame)
                    curGame = None
            elif (option == '0'):  # unregister client
                if (curGame is not None):
                    removeGame(curGame)
                    curGame = None
                break        
    except socket.error:
        print('Lost connection with player: ' + str(getattr(curPlayer, 'name')))
        if (curGame is not None):
            removeGame(curGame)

# accepts connection request from client
def acceptConnection():
    try:
        connection, address = server.accept()
        print('Got connection from', address)
        newPlayer = register(connection)  # add player
        getClientInput(connection, newPlayer, address)  # receive player inputs
        unregister(newPlayer)  # remove player
        connection.close()
    except socket.error:
        print('Could not create connection with client.')

# waits for user input (used to stop server from running)
def getUserInput():
    while True:
        # get user input
        global inputQueue
        userInput = input()
        inputQueue.put(userInput)
        if userInput == 'quit':  # if 'quit', exit thread
            return
        else:  # clear queue for next input
            inputQueue.queue.clear()

# ----------------------------------------------------
# main method functionality
try:
    # setup server socket
    host = socket.gethostbyname(socket.gethostname()) 
    port = 15000
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(20000)
    print('(enter "quit" to exit)\nHost IP: ' + host + '\nPort: ' + str(port) + '\nserver listening...')
except socket.error:
    print('Could not set up server socket. Another application is using the same port.')
    sys.exit(1)

# data structures
inputQueue = queue.Queue()  # holds user input
playerList = []  # holds list of players
gameList = []  # holds list of available games to join

# thread to receive user input while not blocking
inputThread = threading.Thread(target=getUserInput, args=())
inputThread.start()

# listen for connections or "quit" command
while True:
    readList, writeList, exList = select.select([server], [], [], 0.1)    
    for sockInput in readList:    
        # check if got new connection
        if sockInput is server:    
            serverThread = threading.Thread(target=acceptConnection, args=())
            serverThread.daemon = True
            serverThread.start()
    # check if user input 'quit'
    if not inputQueue.empty():   
        if inputQueue.get() == 'quit':
            print('shutting down server...')
            break
