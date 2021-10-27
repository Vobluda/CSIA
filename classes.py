from flask_login import UserMixin

import functions


class Player: #player objects represents each individual player
    id = int #unique id of player
    name = "" #name that players goes by
    defaultChar = "" #the character that is set as default for this player - most players have a specific character they prefer to play, so it will mean less switching in the menu
    school = "" #the school they attend
    seed = 0 #the seed that dictates their placement in the tournament
    currentChar = "" #the character they are currently playing

    def __init__(self, name, defaultChar, school, seed): #initialiser of the player object
        self.name = name
        self.defaultChar = defaultChar
        self.school = school
        self.seed = seed
        self.currentChar = defaultChar


class Game: #the object representing one set of matches (called a game). Each game holds two players that compete in that specific matchup
    id = 0 #the unique id of the game
    seedIndex1 = 0 #an index indicating which player seed should be placed into this game. Used primarily when initially populating the tournament
    seedIndex2 = 0
    player1 = Player #this would be referencing a player object (which player is in this game)
    player2 = Player
    winner = Player #holds the player object of the winner of the game
    score = (0, 0) #a tuple of integers that represents how many games each player has won so far. the first number in the tuple represents the games won by player 1 etc
    bestOf = int #the maximum amount of games possible to be played. Used to determine the amount of games needed to win for a winner to be declared

    def __init__(self, seedIndex1, seedIndex2): #initialiser for the game object. the only things an empty game needs is which seeds it should hold, as it will get populated by a later function
        self.seedIndex1 = seedIndex1
        self.seedIndex2 = seedIndex2
        self.bestOf = 5

    def checkForWinner(self): #method that checks if either player has surpassed the necessary amount of wins to be declared a winner
        if score(0) > int(bestOf/2):
            self.winner = player1
        elif score(1) > int(bestOf/2):
            self.winner = player2
        pass

class Round: #a round object is used to represent a group of games that lead into another round of games. Used when generating the tournament
    games = [] #list of game objects inside the round

class Tournament: #tournament object is used as a container and driver for all subsequent classes. Holds the list of all rounds and a list of all players (used for populating the tournament)
    rounds = [] #list of all round objects
    currentGame = Game #holds a pointer to the current game, so it can be manipulated more easily
    playerList = [] #a list of all players in the tournament, useful for populating the tournament

    def resetBracket(self):
        functions.resetBracket(self)

    def createTournament(self): #function for populating this object with rounds and games in the rounds list to be populated later
        functions.createEmptyTournament(self)

    def populateTournament(self):
        functions.populateEmptyTournament(self)

    def updateTournament(self): #passes over the tournament and updates the bracket (checks for winners and moves winners onto the next game they play)
        functions.updateTournament(self)

    def setCurrentGame(self, id): #scans the tournament for the game with the id asked for by the parameter and then sets a pointer to it into currentGame
        functions.setCurrentGame(self, id)

    def setCurrentGameScore(self, score1, score2):
        functions.setCurrentGameScore(self, score1, score2)

    def setCurrentGameCharacters(self, char1, char2):
        functions.setCurrentGameCharacter(self, char1, char2)

    def setCurrentGameBestOf(self, bestOf):
        functions.setCurrentGameCharacter(self, bestOf)

class PageHandler:
    active = ''
    loggedIn = False
    password = '$2a$12$JhQQvEPl7MwICH6fZYTGVuDLlhjN8n89kPyjcy9V53sFklF66mr5C'

