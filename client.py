#####################################################################
# Game Client
# Developed by Alex van Zuiden-Rylander, Eyas Rashid, and Leighlyn Ha
# Fall Quarter 2019
#####################################################################

import arcade
import socket
import threading
import time
import select

SCREEN_WIDTH = 800  # default width of game window
SCREEN_HEIGHT = 600  # default height of game window
SCREEN_TITLE = "Three Shells and a Pea"  # default title of game window

# game class responsible for running gameplay mechanics
class MyGame(arcade.Window):    
    def __init__(self, clientSocket):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)
        self.username = ' '  # holds player name
        self.serverName = ' '  # holds server IP address
        self.usernameErrMsg = ' '  # status of player name validity
        self.serverNameErrMsg = 'When connecting to a server, the program may hang for \na bit if the server is unavailable.'  # error message for server IP
        self.pageNum = 0  # keeps track of current page 
        self.socket = clientSocket  # handles network socket operations for communicating with server and players
        self.gameListDisplay = ' '  # list of games displayed for current page
        self.gameList = None  # total list of games available
        self.maxGamesPerPage = 30  # max number of games to display on a page
        self.outOfBounds = 2000  # moves objects out of view of player
        self.gameListPageNum = 1  # keeps track of current page of game list
        self.gameCreatedMsg = ' '  # created game status message
        self.gameCreatedWaitMsg = ' '  # created game message to wait for player to join
        self.gameNum = -1  # unique number of game created
        self.listenForPlayerConnection = False  # indicates whether to listen for player connections or not
        self.listenForPlayerResponse = False  # indicates whether to listen for messages from other player or not
        self.gameNumMsg = ' '  # status of joining a game
        self.gameToJoin = ' '  # number of game to join
        self.opponent = ' '  # player name of opponent in game
        self.winningCup = -1  # cup where ball is hidden in
        self.guessedCup = -1  # cup guessed by player
        self.cupHidden = False  # indicates whether player can hide ball in cup
        self.cupGuessed = True  # indicates whether player can guess cup
        self.yourChoiceCupMsg = ' '  # status of player hidden ball
        self.yourGuessCupMsg = 'Waiting for opponent to hide the ball...'  # status of player guess
        self.yourScore = 0  # current player score for game
        self.opponentScore = 0  # opponent player score for game
        self.scoreStatus = ' '  # status message for player score
        self.sentName = False  # indicates whether to send player name to other player
        self.wait = False  # indicates whether to display location of hidden ball
        self.timeElapsed = 0  # indicates how long to display location of hidden ball

        # set up player sprite (cursor)        
        self.player_sprite = arcade.Sprite(r"cursor.png", .0001)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.set_mouse_visible(True)

        # setup menu buttons
        self.listGamesButton = arcade.Sprite(r"list_games.png", 1)
        self.listGamesButton.center_x = 400
        self.listGamesButton.center_y = 1600        
        self.createGameButton = arcade.Sprite(r"create_game.png", 1)
        self.createGameButton.center_x = 400
        self.createGameButton.center_y = 1500
        self.joinGameButton = arcade.Sprite(r"join_game.png", 1)
        self.joinGameButton.center_x = 400
        self.joinGameButton.center_y = 1400

        # setup list games buttons
        self.listGamesNext = arcade.Sprite(r"list_games_next.png", 1)
        self.listGamesNextInBound = 700
        self.listGamesNext.center_x = self.listGamesNextInBound
        self.listGamesNext.center_y = 2100
        self.listGamesPrev = arcade.Sprite(r"list_games_previous.png", 1)
        self.listGamesPrevInBound = 100
        self.listGamesPrev.center_x = self.listGamesPrevInBound
        self.listGamesPrev.center_y = 2100
        self.listGamesBack = arcade.Sprite(r"back.png", 1)
        self.listGamesBack.center_x = 100
        self.listGamesBack.center_y = 2350

        # setup back button for create game page
        self.createGameBack = arcade.Sprite(r"back.png", 1)
        self.createGameBack.center_x = 100
        self.createGameBack.center_y = 2950

        # setup back button for join game page
        self.joinGameBack = arcade.Sprite(r"back.png", 1)
        self.joinGameBack.center_x = 100
        self.joinGameBack.center_y = 3550

        # setup buttons for choose shell page
        self.chooseShellBack = arcade.Sprite(r"back.png", 1)
        self.chooseShellBack.center_x = 100
        self.chooseShellBack.center_y = 4150
        self.chooseCup1 = arcade.Sprite(r"Cup.png", 0.2)
        self.chooseCup1.center_x = SCREEN_WIDTH / 4 + (0 * 220)
        self.chooseCup1X = self.chooseCup1.center_x
        self.chooseCup1.center_y = 3800
        self.chooseCup2 = arcade.Sprite(r"Cup.png", 0.2)
        self.chooseCup2.center_x = SCREEN_WIDTH / 4 + (1 * 220)
        self.chooseCup2X = self.chooseCup2.center_x
        self.chooseCup2.center_y = 3800
        self.chooseCup3 = arcade.Sprite(r"Cup.png", 0.2)
        self.chooseCup3.center_x = SCREEN_WIDTH / 4 + (2 * 220)
        self.chooseCup3X = self.chooseCup3.center_x
        self.chooseCup3.center_y = 3800

        # setup buttons for guess shell page
        self.guessShellBack = arcade.Sprite(r"back.png", 1)
        self.guessShellBack.center_x = 100
        self.guessShellBack.center_y = 4750
        self.guessCup1 = arcade.Sprite(r"Cup.png", 0.2)
        self.guessCup1.center_x = SCREEN_WIDTH / 4 + (0 * 220)
        self.guessCup1X = self.guessCup1.center_x
        self.guessCup1.center_y = 4400
        self.guessCup2 = arcade.Sprite(r"Cup.png", 0.2)
        self.guessCup2.center_x = SCREEN_WIDTH / 4 + (1 * 220)
        self.guessCup2X = self.guessCup2.center_x
        self.guessCup2.center_y = 4400
        self.guessCup3 = arcade.Sprite(r"Cup.png", 0.2)
        self.guessCup3.center_x = SCREEN_WIDTH / 4 + (2 * 220)
        self.guessCup3X = self.guessCup3.center_x
        self.guessCup3.center_y = 4400
        self.ball = arcade.Sprite(r"Ball.jpg", 0.1)
        self.ball.center_x = self.outOfBounds
        self.ball.center_y = 4400

        # setup back button for other player quit page
        self.opponentQuitBack = arcade.Sprite(r"back.png", 1)
        self.opponentQuitBack.center_x = 100
        self.opponentQuitBack.center_y = 5350
    
    # returns characters typed by user
    # charNum = key number typed by user
    # type = (1) check username, (2) check server IP address, (3) check game number inputs
    # returns string equivalent of character typed, or '?' if could not translate character
    def getCharacter(self, charNum, type):
        # convert characters from number pad
        if (charNum >= 65456 and charNum <= 65465) or (charNum == 65454):
            charNum -= 65408
        if (type == 1):  # if we're checking player name values
            if (charNum >= 48 and charNum <= 57) or (charNum >= 97 and charNum <= 122) or (charNum == 32) or (charNum == 46):
                return chr(charNum)
        if (type == 2):  # if we're checking server IP addresses
            if (charNum >= 48 and charNum <= 57) or (charNum == 46):
                return chr(charNum)
        if (type == 3):  # if we're checking game number syntax
            if (charNum >= 48 and charNum <= 57):
                return chr(charNum)
        if (charNum == 65288):  # if backspace pressed
            return 'backspace'
        if (charNum == 65293):  # if enter key pressed
            return 'enter'
        return '?'  # otherwise cannot translate character

    # draws page to get player name (page 0)
    def drawPlayerNamePage(self):        
        arcade.draw_text('Player Name', 340, 500, arcade.color.BLACK, 16)
        arcade.draw_text('Please enter your username:', 300, 340, arcade.color.BLACK, 12)
        arcade.draw_rectangle_outline(400, 300, 400, 30, arcade.color.BLACK, 2, 0)
        arcade.draw_text(self.username, 205, 295, arcade.color.BLACK, 12)
        arcade.draw_text('(Usernames limited to 54 characters)', 280, 240, arcade.color.BLACK, 12)
        arcade.draw_text(self.usernameErrMsg, 260, 220, arcade.color.RED, 12)

    # draws page to get server IP address and connect to server (page 1)
    def drawConnectToServerPage(self):        
        arcade.draw_text('Game Server Name', 300, 1100, arcade.color.BLACK, 16)
        arcade.draw_text('Please enter the IP address of game server to join.\nOnly numbers and "." are accepted.', 250, 940, arcade.color.BLACK, 12)
        arcade.draw_rectangle_outline(400, 900, 400, 30, arcade.color.BLACK, 2, 0)
        arcade.draw_text(self.serverName, 205, 895, arcade.color.BLACK, 12)
        arcade.draw_text('(IP address limited to 15 characters)', 285, 840, arcade.color.BLACK, 12)
        arcade.draw_text(self.serverNameErrMsg, 210, 800, arcade.color.RED, 12)

    # draws menu page with options to list, create, or join game (page 2)
    def drawMenuPage(self):                
        arcade.draw_text('Menu', 350, 1700, arcade.color.BLACK, 30)           
        self.listGamesButton.draw()
        self.createGameButton.draw()
        self.joinGameButton.draw()
    
    # draws page to list available games (page 3)
    def drawGameListPage(self):
        arcade.draw_text('List of Available Games', 280, 2300, arcade.color.BLACK, 20)
        arcade.draw_rectangle_outline(400, 2080, 400, 400, arcade.color.BLACK, 2, 0)
        arcade.draw_text(self.gameListDisplay, 205, 1900, arcade.color.BLACK, 12) 
        self.listGamesNext.draw()   
        self.listGamesPrev.draw()    
        self.listGamesBack.draw() 
    
    # draws page for player to create game and wait for another player to join (page 4)
    def drawCreateGamePage(self):
        arcade.draw_text(self.gameCreatedMsg, 290, 2900, arcade.color.BLACK, 20)
        arcade.draw_text(self.gameCreatedWaitMsg, 275, 2800, arcade.color.BLACK, 12)
        self.createGameBack.draw()

    # draws page for player to join existing game (page 5)
    def drawJoinGamePage(self):
        arcade.draw_text('Join a Game', 300, 3500, arcade.color.BLACK, 30)
        arcade.draw_text('Please type game number of the game you wish to join.\nOnly numbers are acceptable characters.', 230, 3400, arcade.color.BLACK, 12)
        arcade.draw_rectangle_outline(400, 3350, 400, 30, arcade.color.BLACK, 2, 0)
        arcade.draw_text(self.gameToJoin, 205, 3345, arcade.color.BLACK, 12)
        arcade.draw_text(self.gameNumMsg, 230, 3300, arcade.color.RED, 12)
        self.joinGameBack.draw()
    
    # draws page to let player select cup to hide ball in (page 6)
    def drawSelectShellPage(self):
        arcade.draw_text('Hide the Ball in a Cup', 290, 4100, arcade.color.BLACK, 20)
        arcade.draw_text(self.yourChoiceCupMsg, 290, 4050, arcade.color.BLACK, 12)
        self.chooseShellBack.draw()
        self.chooseCup1.draw()
        self.chooseCup2.draw()
        self.chooseCup3.draw()
        arcade.draw_text('1', SCREEN_WIDTH / 4 + (0 * 220), 3700, arcade.color.BLACK, 14)
        arcade.draw_text('2', SCREEN_WIDTH / 4 + (1 * 220), 3700, arcade.color.BLACK, 14)
        arcade.draw_text('3', SCREEN_WIDTH / 4 + (2 * 220), 3700, arcade.color.BLACK, 14)
        arcade.draw_text('Opponent: ' + self.opponent, 500, 3650, arcade.color.BLACK, 12)
        arcade.draw_text('Your Score: ' + str(self.yourScore), 50, 3650, arcade.color.BLACK, 12)
        arcade.draw_text('Opponent Score: ' + str(self.opponentScore), 50, 3630, arcade.color.BLACK, 12)
        arcade.draw_text(self.scoreStatus, 200, 3640, arcade.color.BLACK, 12)
    
    # draws page to let player guess cup that ball is hidden in (page 7)
    def drawGuessShellPage(self):
        arcade.draw_text('Guess Which Cup Hides the Ball', 270, 4700, arcade.color.BLACK, 20)
        arcade.draw_text(self.yourGuessCupMsg, 290, 4650, arcade.color.BLACK, 12)
        self.guessShellBack.draw()        
        self.guessCup1.draw()
        self.guessCup2.draw()
        self.guessCup3.draw()
        arcade.draw_text('1', SCREEN_WIDTH / 4 + (0 * 220), 4300, arcade.color.BLACK, 14)
        arcade.draw_text('2', SCREEN_WIDTH / 4 + (1 * 220), 4300, arcade.color.BLACK, 14)
        arcade.draw_text('3', SCREEN_WIDTH / 4 + (2 * 220), 4300, arcade.color.BLACK, 14)
        arcade.draw_text('Opponent: ' + self.opponent, 500, 4250, arcade.color.BLACK, 12)
        arcade.draw_text('Your Score: ' + str(self.yourScore), 50, 4250, arcade.color.BLACK, 12)
        arcade.draw_text('Opponent Score: ' + str(self.opponentScore), 50, 4230, arcade.color.BLACK, 12)
        arcade.draw_text(self.scoreStatus, 200, 4240, arcade.color.BLACK, 12)
        self.ball.draw()
    
    # draws page when opponent exits game (page 8)
    def drawPlayerQuitPage(self):
        arcade.draw_text('OOPS! Looks like your opponent has exited the game!', 110, 5200, arcade.color.BLACK, 20)
        self.opponentQuitBack.draw()

    # renders all pages
    def on_draw(self):
        arcade.start_render()
        self.player_sprite.draw()
        self.drawPlayerNamePage()    
        self.drawConnectToServerPage()
        self.drawMenuPage()
        self.drawGameListPage()
        self.drawCreateGamePage()
        self.drawJoinGamePage()
        self.drawSelectShellPage()
        self.drawGuessShellPage()
        self.drawPlayerQuitPage()
    
    # updates objects on page
    def update(self, delta_time):
        # determines which page to display
        if (self.pageNum == 0):  # get player name page
            self.set_viewport(0, 800, 0, 600)
        elif (self.pageNum == 1):  # connect to server page
            self.set_viewport(0, 800, 600, 1200)        
        elif (self.pageNum == 2):  # game menu page
            self.set_viewport(0, 800, 1200, 1800)
        elif (self.pageNum == 3):  # list games page
            self.set_viewport(0, 800, 1800, 2400)
        elif (self.pageNum == 4):  # create game page
            self.set_viewport(0, 800, 2400, 3000)
        elif (self.pageNum == 5):  # join game page
            self.set_viewport(0, 800, 3000, 3600)
        elif (self.pageNum == 6):  # choose shell page
            self.set_viewport(0, 800, 3600, 4200)
        elif (self.pageNum == 7):  # guess shell page
            self.set_viewport(0, 800, 4200, 4800)
        elif (self.pageNum == 8):  # opponent player quit page
            self.set_viewport(0, 800, 4800, 5400)

        # displays page with location of ball for given time
        if (self.wait):
            if (self.timeElapsed < 8):  # display answer for set amount of time
                self.timeElapsed += 0.1
            else:  # reset timer and display next page
                self.timeElapsed = 0
                self.pageNum = 6
                self.wait = False

        # listen for player connection if waiting for one
        if (self.listenForPlayerConnection):  
            # if connection made, remove game from server and accept connection
            if (self.socket.waitForPlayerConnection()):
                self.listenForPlayerConnection = False
                self.socket.removeGameFromServer()
                self.socket.acceptPlayerConnection()
                self.listenForPlayerResponse = True
                self.pageNum = 6
            else:
                self.listenForPlayerConnection = True

        # listen for response from other player
        if (self.listenForPlayerResponse):  
            if (self.socket.waitForPlayerResponse()):  # if received response
                response = self.socket.readPlayerResponse()
                self.parseResponse(response)
            else:
                self.listenForPlayerResponse = True

    # parses message received from other player
    def parseResponse(self, response):  
        if (response is None):
            return      
        if (response == 'quit'):  # if quit message, exit game
            self.listenForPlayerResponse = False
            self.wait = False
            self.timeElapsed = 0
            self.pageNum = 8
        elif (response[0] == '\n'):  # received opponent player name
            self.opponent = response[1:]
            if (not self.sentName):  # if haven't sent player name, send it
                self.socket.sendMessageToPlayer('\n' + self.username)
                self.sentName = True
        elif (response[0] == 's'):  # received opponent score
            prevScore = self.opponentScore
            self.opponentScore = int(response[1:])
            if (prevScore < self.opponentScore):
                self.scoreStatus = 'Your opponent guessed right!'
            else:
                self.scoreStatus = 'Your opponent guessed wrong!'
        elif (response[0] == 'g'):  # received opponent guess (cup number), move to guess cup page
            self.guessedCup = int(response[1:])
            self.cupHidden = False
            self.cupGuessed = True
            self.yourChoiceCupMsg = ' '
            self.yourGuessCupMsg = 'Waiting for opponent to hide the ball...'
            self.guessCup1.center_x = self.guessCup1X
            self.guessCup2.center_x = self.guessCup2X
            self.guessCup3.center_x = self.guessCup3X
            self.ball.center_x = self.outOfBounds
            self.chooseCup1.center_x = self.chooseCup1X
            self.chooseCup2.center_x = self.chooseCup2X
            self.chooseCup3.center_x = self.chooseCup3X
            self.pageNum = 7
        elif (response[0] == 'c'):  # received cup number ball is hidden in, let player guess cup
            self.winningCup = int(response[1:])
            self.yourGuessCupMsg = 'Opponent has hidden the ball.'
            self.cupGuessed = False

    # handles key press event for user input
    def on_key_press(self, key, modifiers):       
        if (self.pageNum == 0):  # if getting player name
            self.validateUsernameInput(key)
        elif (self.pageNum == 1):  # if getting server IP address
            self.validateServerNameInput(key)
        elif (self.pageNum == 5):  # if getting game number to join
            self.validateGameNumInput(key)

    # handles functionality when user clicks on button
    def on_mouse_press(self, x, y, button, modifiers):        
        self.player_sprite.center_x = x
        if (self.pageNum == 2):  # menu page
            self.player_sprite.center_y = y + 1200
            self.clickMenuOption()
        elif (self.pageNum == 3):  # game list page
            self.player_sprite.center_y = y + 1800
            self.clickGameListButton()
        elif (self.pageNum == 4):  # create game page
            self.player_sprite.center_y = y + 2400
            self.clickCreateGameBack()
        elif (self.pageNum == 5):  # join game page
            self.player_sprite.center_y = y + 3000
            self.clickJoinGameBack()
        elif (self.pageNum == 6):  # choose cup page
            self.player_sprite.center_y = y + 3600
            self.clickChooseShellBack()
            self.chooseCup()
        elif (self.pageNum == 7):  # guess cup page
            self.player_sprite.center_y = y + 4200
            self.clickGuessShellBack()
            self.guessCup()
        elif (self.pageNum == 8):  # player quit page
            self.player_sprite.center_y = y + 4800
            self.clickPlayerQuitBack()

    # handles functionality for user to hide ball in cup (for page 6)
    def chooseCup(self):
        if (not self.cupHidden):  # if player has not selected cup yet
            # check which cup player clicked on, remove cup to indicate selection
            if (arcade.check_for_collision(self.player_sprite, self.chooseCup1)):
                self.winningCup = 1
                self.chooseCup1.center_x = self.outOfBounds
            elif (arcade.check_for_collision(self.player_sprite, self.chooseCup2)):
                self.winningCup = 2
                self.chooseCup2.center_x = self.outOfBounds
            elif (arcade.check_for_collision(self.player_sprite, self.chooseCup3)):
                self.winningCup = 3      
                self.chooseCup3.center_x = self.outOfBounds          
            else:
                return
            self.cupHidden = True  # update status so player can't select another cup
            self.yourChoiceCupMsg = 'You chose Cup: ' + str(self.winningCup) + '\nWaiting for opponent to guess...' 
            self.socket.sendMessageToPlayer('c' + str(self.winningCup))  # send cup choice to opponent

    # handles functionality for user to guess cup ball is hidden in (for page 7)
    def guessCup(self):
        if (not self.cupGuessed):  # if player is allowed to guess a cup   
            # check which cup player selected   
            if (arcade.check_for_collision(self.player_sprite, self.guessCup1)):
                self.guessedCup = 1
            elif (arcade.check_for_collision(self.player_sprite, self.guessCup2)):
                self.guessedCup = 2
            elif (arcade.check_for_collision(self.player_sprite, self.guessCup3)):
                self.guessedCup = 3        
            else:
                return
            self.cupGuessed = True  # set status so player can't select different cup
            self.yourGuessCupMsg = 'You guessed Cup: ' + str(self.guessedCup) + '\nAnswer: ' + str(self.winningCup) 
            if (self.guessedCup == self.winningCup):  # update score
                self.yourScore += 1
            else:
                self.yourScore -= 1
            # show location of correct answer (where ball is hidden)
            if (self.winningCup == 1):
                self.guessCup1.center_x = self.outOfBounds
                self.ball.center_x = self.guessCup1X
            elif (self.winningCup == 2):
                self.guessCup2.center_x = self.outOfBounds
                self.ball.center_x = self.guessCup2X
            elif (self.winningCup == 3):
                self.guessCup3.center_x = self.outOfBounds
                self.ball.center_x = self.guessCup3X
            self.socket.sendMessageToPlayer('s' + str(self.yourScore))  # send score to opponent
            self.socket.sendMessageToPlayer('g' + str(self.guessedCup))  # send guess to opponent
            self.wait = True  # set status to give player time to view correct answer

    # check if player clicked on menu button (for page 2)
    def clickMenuOption(self):
        # if player clicked on list games button
        if (arcade.check_for_collision(self.player_sprite, self.listGamesButton)):
            self.getGameList()
        # if player clicked on create game button
        elif (arcade.check_for_collision(self.player_sprite, self.createGameButton)):
            self.createGame()     
        # if player clicked on join game button
        elif (arcade.check_for_collision(self.player_sprite, self.joinGameButton)):
            self.pageNum = 5

    # if player clicked on list game button, display list of available games 
    def clickGameListButton(self):
        firstGameDisplayed = 0
        lastGameDisplayed = 0
        tempGameList = ''
        # if pressed the next button
        if (arcade.check_for_collision(self.player_sprite, self.listGamesNext)):            
            # if there are more games to display
            if (self.gameListPageNum * self.maxGamesPerPage < len(self.gameList)):
                firstGameDisplayed = self.gameListPageNum * self.maxGamesPerPage
                self.gameListPageNum += 1
                # if there are more games to display in the next page
                if (self.gameListPageNum * self.maxGamesPerPage < len(self.gameList)):
                    lastGameDisplayed = self.gameListPageNum * self.maxGamesPerPage
                    self.listGamesNext.center_x = self.listGamesNextInBound
                else:
                    lastGameDisplayed = len(self.gameList)
                    self.listGamesNext.center_x = self.outOfBounds
                # if there were previous games displayed on a previous page
                if (self.gameListPageNum > 1):
                    self.listGamesPrev.center_x = self.listGamesPrevInBound
                else:
                    self.listGamesPrev.center_x = self.outOfBounds
                # display the list of games for the current page
                for index in range(firstGameDisplayed, lastGameDisplayed):
                    tempGameList += self.gameList[index]
                self.gameListDisplay = tempGameList
        # if pressed the previous button
        elif (arcade.check_for_collision(self.player_sprite, self.listGamesPrev)):
            # if we're not at the first page in the game list
            if (self.gameListPageNum > 1):
                self.gameListPageNum -= 1
                lastGameDisplayed = self.gameListPageNum * self.maxGamesPerPage
                firstGameDisplayed = (self.gameListPageNum - 1) * self.maxGamesPerPage
                self.listGamesNext.center_x = self.listGamesNextInBound
                # if we're at first page, hide previous button, else display it
                if (self.gameListPageNum == 1):
                    self.listGamesPrev.center_x = self.outOfBounds
                else:
                    self.listGamesPrev.center_x = self.listGamesPrevInBound
                # display list of games for current page
                for index in range(firstGameDisplayed, lastGameDisplayed):
                    tempGameList += self.gameList[index]
                self.gameListDisplay = tempGameList
        # if back button was pressed, return to menu
        elif (arcade.check_for_collision(self.player_sprite, self.listGamesBack)):
            self.gameListPageNum = 1
            self.pageNum = 2

    # if player clicked on back button from create game page (page 4),
    # return to main menu (page 2)
    def clickCreateGameBack(self):
        if (arcade.check_for_collision(self.player_sprite, self.createGameBack)):
            self.listenForPlayerConnection = False
            self.socket.removeGameFromServer()  # remove game from server
            self.socket.closeGameConnection() # close connection with other player (if exists)
            self.pageNum = 2

    # if player clicked on back button from join game page (page 5),
    # return to main menu (page 2)
    def clickJoinGameBack(self):
        if (arcade.check_for_collision(self.player_sprite, self.joinGameBack)):
            self.gameNumMsg = ' '
            self.gameToJoin = ' '
            self.pageNum = 2
    
    # if player clicked on back button from choosing cup (hide ball) page (page 6),
    # return to main menu (page 2)
    def clickChooseShellBack(self):
        if (arcade.check_for_collision(self.player_sprite, self.chooseShellBack)):
            # close game connection with other player
            self.socket.closeGameConnection()  
            # reset page variables
            self.listenForPlayerResponse = False
            self.gameNumMsg = ' '
            self.gameToJoin = ' '
            self.sentName = False
            self.scoreStatus = ' '
            self.yourScore = 0
            self.opponentScore = 0
            self.opponent = ' '
            self.yourChoiceCupMsg = ' '
            self.yourGuessCupMsg = 'Waiting for opponent to hide the ball...'
            self.guessCup1.center_x = self.guessCup1X
            self.guessCup2.center_x = self.guessCup2X
            self.guessCup3.center_x = self.guessCup3X
            self.ball.center_x = self.outOfBounds
            self.chooseCup1.center_x = self.chooseCup1X
            self.chooseCup2.center_x = self.chooseCup2X
            self.chooseCup3.center_x = self.chooseCup3X
            self.winningCup = 0
            self.guessedCup = 0
            self.wait = False
            self.cupGuessed = True
            self.cupHidden = False
            self.pageNum = 2
    
    # if player clicked on back button from guessing cup page (page 7),
    # return to main menu (page 2)
    def clickGuessShellBack(self):
        if (arcade.check_for_collision(self.player_sprite, self.guessShellBack)):
            # close connection with other player
            self.socket.closeGameConnection()
            # reset page variables
            self.listenForPlayerResponse = False
            self.gameNumMsg = ' '
            self.gameToJoin = ' '
            self.sentName = False
            self.scoreStatus = ' '
            self.yourScore = 0
            self.opponentScore = 0
            self.opponent = ' '
            self.yourChoiceCupMsg = ' '
            self.yourGuessCupMsg = 'Waiting for opponent to hide the ball...'
            self.guessCup1.center_x = self.guessCup1X
            self.guessCup2.center_x = self.guessCup2X
            self.guessCup3.center_x = self.guessCup3X
            self.ball.center_x = self.outOfBounds
            self.chooseCup1.center_x = self.chooseCup1X
            self.chooseCup2.center_x = self.chooseCup2X
            self.chooseCup3.center_x = self.chooseCup3X
            self.winningCup = 0
            self.guessedCup = 0
            self.wait = False
            self.cupGuessed = True
            self.cupHidden = False
            self.pageNum = 2

    # if player clicked back button on player quit page (page 8),
    # return to main menu (page 2)
    def clickPlayerQuitBack(self):
        if (arcade.check_for_collision(self.player_sprite, self.opponentQuitBack)):
            self.listenForPlayerResponse = False
            # close connection with other player (if exists)
            self.socket.closeGameConnection()
            # reset page variables
            self.gameNumMsg = ' '
            self.gameToJoin = ' '
            self.sentName = False
            self.scoreStatus = ' '
            self.yourScore = 0
            self.opponentScore = 0
            self.opponent = ' '
            self.yourChoiceCupMsg = ' '
            self.yourGuessCupMsg = 'Waiting for opponent to hide the ball...'
            self.guessCup1.center_x = self.guessCup1X
            self.guessCup2.center_x = self.guessCup2X
            self.guessCup3.center_x = self.guessCup3X
            self.ball.center_x = self.outOfBounds
            self.chooseCup1.center_x = self.chooseCup1X
            self.chooseCup2.center_x = self.chooseCup2X
            self.chooseCup3.center_x = self.chooseCup3X
            self.winningCup = 0
            self.guessedCup = 0
            self.wait = False
            self.cupGuessed = True
            self.cupHidden = False
            self.pageNum = 2

    # gets list of available games from server
    def getGameList(self):
        self.gameList = self.socket.requestGameList()  # get game list from server
        if (self.gameList is None):  # connection lost with server
            self.gameListDisplay = 'OOPS! You have lost connection with the game server.'
            self.listGamesNext.center_x = self.outOfBounds
            self.listGamesPrev.center_x = self.outOfBounds
        elif (self.gameList[0] == '-1'):  # no games available
            self.gamesList = None
            self.gameListDisplay = 'Sorry, no games available...'
            self.listGamesNext.center_x = self.outOfBounds
            self.listGamesPrev.center_x = self.outOfBounds
        else:  # at least 1 game available
            listOfGames = ''
            lastGameDisplayed = 0
            # if number of games is less than max number of games to display per page
            if (len(self.gameList) <= self.maxGamesPerPage):
                self.listGamesNext.center_x = self.outOfBounds
                self.listGamesPrev.center_x = self.outOfBounds
                lastGameDisplayed = len(self.gameList)
            else:  # display only max number of games per page
                self.listGamesNext.center_x = self.listGamesNextInBound
                self.listGamesPrev.center_x = self.outOfBounds
                lastGameDisplayed = self.maxGamesPerPage
            # populate string to display games on page
            for index in range(lastGameDisplayed):
                listOfGames += self.gameList[index]
            self.gameListDisplay = listOfGames
        self.pageNum = 3  # go to display game list page

    # create game for player on server
    def createGame(self):
        if (not self.socket.hostGame()): # create socket for hosting game
            self.gameCreatedMsg = 'Game could not be created!'
            self.gameCreatedWaitMsg = 'If you have a duplicate of this game open,\nplease close it and try again.'        
        else:  # notify server to create a game
            gameNum = self.socket.createGameOnServer()
            if (gameNum == -1):  # if lost connection with server
                self.gameCreatedMsg = 'Game could not be created!'
                self.gameCreatedWaitMsg = 'You have lost connection with the game server.'
            else:  # game successfully created on server
                self.gameNum = gameNum
                self.gameCreatedMsg = 'Game ' + str(self.gameNum) + ' created!'
                self.gameCreatedWaitMsg = 'Waiting for another player to connect...'   
                self.listenForPlayerConnection = True
        self.pageNum = 4  # display create game page   

    # let player join available game on server
    def joinGame(self):
        gameHostAddr = self.socket.getPlayerIP(self.gameToJoin)  # get IP address of player hosting game
        if (gameHostAddr == '-2'):  # if lost connection with game server
            self.gameNumMsg = 'OOPS! You have lost connection with the game server.'
        elif (gameHostAddr == '-1'):  # if game is not available to play (not valid game number)
            self.gameNumMsg = 'Sorry, that game is not available to play.\nPlease type another game number to join.'
        else:  # game exists on server
            self.gameNumMsg = 'Connecting to player server.\nProgram may hang if server is unavailable.'
            if (not self.socket.connectToPlayerServer()):  # connect to player hosting game
                self.gameNumMsg = 'Unable to join game. Player server is unavailable.'
            else:  # if connection to player successful
                self.listenForPlayerResponse = True              
                if (not self.socket.sendMessageToPlayer('\n' + self.username)):  # send player name to other player
                    self.gameNumMsg = 'Unable to join game. Player server is unavailable.'
                else:  # if player name successfully sent
                    self.sentName = True
                    self.pageNum = 7

    # connects to game server
    def joinServer(self):
        if (self.socket.connectToGameServer(self.serverName)):  # connect to server                   
            if (self.socket.registerPlayer(self.username)):  # register player
                self.pageNum = 2
            else:  # if failed to register player
                self.serverNameErrMsg = 'Failed to register player name with server. Server is unavailable.'
        else:  # if failed to connect to server
            self.serverNameErrMsg = 'Failed to connect to server. Either the IP address is wrong or \nthe server is unavailable.'

    # checks input for game number
    def validateGameNumInput(self, key):
        char = self.getCharacter(key, 3)  # translate key press to character
        if (self.gameToJoin == ' '):  # if first character in string
            if not(char == '?' or char == 'backspace' or char == 'enter'):
                self.gameToJoin = char
            if (char == 'enter'):
                self.gameNumMsg = 'Game number must not be blank or only whitespace.'
        else:  # if not first character in string
            if not(char == '?' or char == 'backspace' or char == 'enter') and (len(self.gameToJoin) < 20):
                self.gameToJoin += char
            if (char == 'backspace'):  # if backspace pressed
                if (len(self.gameToJoin) == 1):
                    self.gameToJoin = ' '
                if (len(self.gameToJoin) > 1):
                    self.gameToJoin = self.gameToJoin[:-1]
            if (char == 'enter'):  # if enter key pressed
                if (len(self.gameToJoin) <= 0) or (self.gameToJoin.isspace()):
                    self.gameNumMsg = 'Game number must not be blank or only whitespace.'
                else:  # input is a number, try to join game
                    self.joinGame()

    # check input for server IP address
    def validateServerNameInput(self, key):
        char = self.getCharacter(key, 2)  # translate key press to character
        if (self.serverName == ' '):  # if first character in string
            if not(char == '?' or char == 'backspace' or char == 'enter'):
                self.serverName = char
            if (char == 'enter'):
                self.serverNameErrMsg = 'Server IP address must not be blank or only whitespace'
        else:  # if not first character in string
            if not(char == '?' or char == 'backspace' or char == 'enter') and (len(self.serverName) < 15):
                self.serverName += char
            if (char == 'backspace'):  # if backspace pressed
                if (len(self.serverName) == 1):
                    self.serverName = ' '
                if (len(self.serverName) > 1):
                    self.serverName = self.serverName[:-1]
            if (char == 'enter'):  # if enter key pressed
                if (len(self.serverName) <= 0) or (self.serverName.isspace()):
                    self.serverNameErrMsg = 'Server IP address must not be blank or only whitespace'
                else:  # if input is valid IP address, try to connect to server
                    self.joinServer()

    # check input for player name
    def validateUsernameInput(self, key):
        char = self.getCharacter(key, 1)  # translate key press to character
        if (self.username == ' '):  # if first character in string 
            if not(char == '?' or char == 'backspace' or char == 'enter'):
                self.username = char
            if (char == 'enter'):
                self.usernameErrMsg = 'Username must not be blank or only whitespace'
        else:  # if not first character in string
            if not(char == '?' or char == 'backspace' or char == 'enter') and (len(self.username) < 54):
                self.username += char
            if (char == 'backspace'):  # if backspace pressed
                if (len(self.username) == 1):
                    self.username = ' '
                if (len(self.username) > 1):
                    self.username = self.username[:-1]
            if (char == 'enter'):  # if enter key pressed
                if (len(self.username) <= 0) or (self.username.isspace()):
                    self.usernameErrMsg = 'Username must not be blank or only whitespace'
                else:  # if input is valid player name
                    self.pageNum = 1

# handles socket communications between game server and players
class SocketConnection():
    def __init__(self):
        self.clientSd = None  # socket descriptor for connection with server
        self.playerSd = None  # socket descriptor for running player server
        self.host = ' '  # IP address of game server to connect to
        self.port = 0  # port number of game server to connect to
        self.gameHost = ' '  # IP address of game server hosted by this player
        self.gamePort = 15001  # port number of game server hosted by this player
        self.peerHostAddr = ' '  # IP address of player to connect to
        self.hasConnectionServer = False  # indicates if player is connected to game server
        self.peerConnection = None  # connection object used for communication between players
        self.printConnectionIssue = True  # prevents repeated printing of same connection issue

    # connect to game server given server IP address (serverName)
    def connectToGameServer(self, serverName):
        # set up connection to server
        self.clientSd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = serverName 
        self.port = 15000        
        try:
            # connect to server
            self.clientSd.connect((self.host, self.port)) 
            self.hasConnectionServer = True
            return True
        except socket.error:
            print('Unable to connect to game server: ' + serverName)
        return False

    # connect to game server hosted by player
    def connectToPlayerServer(self):
        try:
            # connect to other player hosting game
            self.peerConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
            self.peerConnection.connect((self.peerHostAddr, self.gamePort))            
            return True
        except socket.error:
            print('Unable to connect to player server ' + self.peerHostAddr)
        return False

    # send given message to other player
    def sendMessageToPlayer(self, message):
        try:
            # append '\r' to indicate end of message
            newMessage = str(message) + '\r'
            self.peerConnection.send(newMessage.encode())  # send message
            return True
        except socket.error:
            print('Unable to send message to player. Lost connection.')
        return False

    # create game server on local player IP address
    def hostGame(self):
        try:
            # setup game server
            self.gameHost = socket.gethostbyname(socket.gethostname()) 
            self.playerSd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.playerSd.bind((self.gameHost, self.gamePort))
            self.playerSd.listen(1)
            return True
        except socket.error:
            print('Failed to set up game host socket. Port 15001 is already being used by another application.')
        return False

    # listen for another player connecting to game server
    # this method was meant to be called repeatedly in MyGame class update method
    def waitForPlayerConnection(self):
        try:
            # use non-blocking method to check for connections
            readList, writeList, exList = select.select([self.playerSd], [], [], 0.01)    
            for sockInput in readList:    
                # check if got new connection
                if (sockInput is self.playerSd):  
                    return True
        except socket.error:
            print('Unable to listen for player connection.')
        return False    
    
    # accept incoming player connection if received one
    def acceptPlayerConnection(self):
        try:
            # accept connection from other player
            self.peerConnection, address = self.playerSd.accept()
            return True
        except socket.error:
            print('Failed to accept peer connection.')
        return False

    # listen for messages from other player
    # this was meant to be called repeatedly in MyGame class update method
    def waitForPlayerResponse(self):
        try:
            # use non-blocking method to check for messages from other player
            readList, writeList, exList = select.select([self.peerConnection], [], [], 0.01)    
            for sockInput in readList:    
                # check if got message from other player
                if (sockInput is self.peerConnection):  
                    return True
        except socket.error:
            print('Unable to listen for player response')
        return False 

    # read message sent from other player
    def readPlayerResponse(self):
        try:
            # read response character by character and stop at '\r'
            response = ''
            char = self.peerConnection.recv(1).decode('utf-8')
            while char != '\r':
                response += char
                char = self.peerConnection.recv(1).decode('utf-8')
            self.printConnectionIssue = True
            return response
        except socket.error:
            if (self.printConnectionIssue):
                print('Unable to read data from other player.')
                self.printConnectionIssue = False
        return None

    # notify game server to remove game from list of games
    def removeGameFromServer(self):
        try:
            self.clientSd.send('4'.encode())
            return True
        except socket.error:
            print('Could not remove game from server. Lost connection.')
        return False

    # send player name to register player on server
    def registerPlayer(self, playerName):
        name = str(playerName)
        name += '\r'  # indicates end of player name
        try:            
            self.clientSd.send(name.encode())
            return True
        except socket.error:
            print('Could not send playername to server. Lost connection.')
        return False

    # get list of available games from server
    # return list of availab games on server
    def requestGameList(self):
        try:
            # send request for game list from server
            self.clientSd.send('1'.encode())
            # read list of games returned from server
            tempList = ''
            gamesList = None
            char = self.clientSd.recv(1).decode('utf-8')
            while char != '\r':
                tempList += char
                char = self.clientSd.recv(1).decode('utf-8')
            # if there is at least 1 game available, add all games to game list
            if (tempList != '') and (tempList != '-1'):
                gamesList = tempList.split('\n')
                for index in range(len(gamesList)):
                    gamesList[index] += '\n'
                del gamesList[-1]
            if (tempList == '-1'):  # if no games available
                gamesList = ['-1']
            return gamesList
        except socket.error:
            print('Unable to get game list from server. Lost connection.')
        return None

    # create game on server, returns number of game created
    def createGameOnServer(self):
        try:
            # send request to create new game on server
            self.clientSd.send('2'.encode())
            # read game number from server
            gameNum = ''
            char = self.clientSd.recv(1).decode('utf-8')
            while char != '\r':
                gameNum += char
                char = self.clientSd.recv(1).decode('utf-8')
            return int(gameNum)
        except socket.error:
            print('Failed to create game on server. Lost connection.')
        return -1

    # gets IP address of player hosting game to join
    # return IP address of player hosting game
    def getPlayerIP(self, gameNum):
        try:
            # send request to server to join game
            self.clientSd.send('3'.encode())
            # send game number to join
            tempGameNum = str(gameNum) + '\r'
            self.clientSd.send(tempGameNum.encode())
            # read IP address of player hosting game
            tempGameHostAddr = ''
            char = self.clientSd.recv(1).decode('utf-8')
            while char != '\r':
                tempGameHostAddr += char
                char = self.clientSd.recv(1).decode('utf-8')
            self.peerHostAddr = tempGameHostAddr
            return tempGameHostAddr
        except socket.error:
            print('Unable to join player game on server. Lost connection.')
        return '-2'

    # close connection with player hosting game (exit game)
    def closeGameConnection(self):
        if (self.peerConnection is not None):
            try:
                # send quit message to other player
                self.peerConnection.send('quit\r'.encode())
                # tell server to remove game (if not already removed)
                self.clientSd.send('4'.encode())
            except socket.error:
                print('Game connection already closed.')
            finally:
                # close connection with other player
                self.peerConnection.close()
                self.peerConnection = None
                # close game server running on player (if player is game host)
                if (self.playerSd is not None):
                    self.playerSd.close()
                    self.playerSd = None

    # close connection with game server
    def closeConnection(self):
        if (self.hasConnectionServer and self.clientSd is not None):
            try:
                # close connection with any ongoing game with another player
                self.closeGameConnection()                
                self.clientSd.send('0'.encode())  # send exit message to server
                self.clientSd.close()  # close connection with server
                return True
            except socket.error:
                print('Server connection already closed.')
        return False

# runs game
def main():
    # create SocketConnection object to handle game connections
    clientSocket = SocketConnection()
    # create game
    myGame = MyGame(clientSocket)
    arcade.run()
    # if game exitted, close any remaining connections
    clientSocket.closeConnection()

if __name__ == "__main__":
    main()
