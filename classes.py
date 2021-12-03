import math
import random
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


class Game: #the object representing one set of matches (called a game).
    # Each game holds two players that compete in that specific matchup
    id = 0 #the unique id of the game
    seedIndex1 = 0 #an index indicating which player seed should be placed
    # into this game. Used primarily when initially populating the tournament
    seedIndex2 = 0
    player1 = Player #this would be referencing a player object (which player
    # is in this game)
    player2 = Player
    winner = Player #holds the player object of the winner of the game
    score = (0, 0) #a tuple of integers that represents how many games each
    # player has won so far. the first number in the tuple represents the games
    # won by player 1 etc
    bestOf = int #the maximum amount of games possible to be played. Used to
    # determine the amount of games needed to win for a winner to be declared

    def __init__(self, seedIndex1, seedIndex2): #initialiser for the game object.
        # the only things an empty game needs is which seeds it should hold, as
        # it will get populated by a later function
        self.seedIndex1 = seedIndex1
        self.seedIndex2 = seedIndex2
        self.bestOf = 5

    def checkForWinner(self): #method that checks if either player has surpassed
        # the necessary amount of wins to be declared a winner
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

    def sanitizePlayerList(self):  # this function is used to 'sanitize' the user input into the playerlist (such as invalid seeding or not enough players to make a tournament)
        playerList = self.playerList

        i = 0  # the following chunk of code is used to remove any 'Null' players that represent byes. These are removed because if a tournament is created on top of an already existing tournament (i.e. to update seeding etc.) the 'Null' players still remain, causing problems
        while i < len(playerList):  # iterates over playerList and if any player has a name 'Null' they are removed
            if playerList[i].name == 'Null':
                del playerList[i]
            else:
                i += 1

        takenSeeds = []  # creates a list that will store all seeds being used already
        for player in playerList:  # iterates over every player in the playerlist
            player.seed = int(player.seed)
            if player.seed is None:  # the following will set the seed to 0 (to be changed in the future) if the seed is None, already taken by a previous player or not a valid seed (i.e. below 0 or over the amount players in the playerList)
                player.seed = 0
            elif player.seed in takenSeeds:
                player.seed = 0
            elif player.seed <= 0 or player.seed > len(playerList):
                player.seed = 0
            else:
                takenSeeds.append(
                    player.seed)  # if a player's seed satisfies the above, their seed is added to the list of already taken seeds so further players can't use it

        availableSeeds = []  # based on the list of already taken seeds, another list containing valid seeds that are not being used is created
        for i in range(1, len(playerList) + 1):
            if i not in takenSeeds:
                availableSeeds.append(i)

        random.shuffle(availableSeeds)  # these available seeds are shuffled (i.e. random order) so that there is no bias towards early entries when randomly seeding.

        for player in playerList:  # iterates over the playerlist and any players with a seed of 0 (from before) are now given a random available seed
            if player.seed == 0:
                player.seed = availableSeeds[0]
                del availableSeeds[0]

        seedCounter = 1  # the following adds the remaining 'null' players that represent an automatic win to the next round (necessary as each bracket needs a power of 2 amount of players)
        while math.log2(len(playerList)) != math.floor(math.log2(len(playerList))):  # while the amount of players in the playerlist is not an exponent of 2
            playerList.append(Player("Null", "", "", len(playerList) + seedCounter))  # creates a 'null' character, which can later be checked for as an automatic win
            seedCounter += 1

        functions.addIdsToPlayerList(playerList)  # finally, it adds ids to the players again so that 'Null' players are also given ids

    def resetBracket(self): #function to clear the tournament object of rounds and games, so a new
        # bracket can be created
        if self.rounds is not None:  # as long as the tournament isn't empty
            self.rounds.clear()  # removes all the round objects in the tournament
        self.rounds = []  # it then resets tournament.rounds to a list, because .clear() doesn't leave
        # a list behind, but instead Null

    def createTournament(self): #function for populating this object with rounds and games in the
        # rounds list to be populated later
        playerList = self.playerList
        roundNumber = int(math.ceil(math.log(len(playerList),
                                             2)))  # find the lowest possible round number (log base 2
        # of the amount of players rounded up)
        for currentRound in range(0, roundNumber):  # loop over the round indices
            self.rounds.append(Round())  # appends a new round object to the rounds list
            if currentRound == 0:  # if the current round is the first one created
                self.rounds[currentRound].games = [Game(1, 2)]  # add the final game (seeing as the bracket is created backwards)
            else:
                for currentGame in range(int(2 ** currentRound)):  # iterates over the necessary amount of games per round (number of games is derived by the round number)
                    if currentGame % 2 == 0:  # if the game number is even
                        seedIndex1 = self.rounds[currentRound - 1].games[currentGame // 2].seedIndex1  # the seedindex1 for this game is derived from the previous games' seedindex1
                    else:
                        seedIndex1 = self.rounds[currentRound - 1].games[currentGame // 2].seedIndex2  # if the game is odd, the seedindex1 for this game is derived from the previous games' seedindex2
                    seedIndex2 = int(2 ** (currentRound + 1)) + 1 - seedIndex1  # the other seed index is derived as the opposite of the seeding of the seedindex1 (so if seedindex1 is the 1st seed in a round with 8 players, seedindex2 would be the 8th seed)
                    self.rounds[currentRound].games.append(Game(seedIndex1, seedIndex2))  # adds this created game to the respective round it belongs to
        self.rounds = self.rounds[::-1]  # after all games and rounds have been created, the round order
        # is flipped to create the conventional bracket structure
        gameIDCounter = 0
        for curr_round in self.rounds:  # iterates over all games and gives each game a unique id
            for curr_game in curr_round.games:
                gameIDCounter += 1
                curr_game.id = gameIDCounter

    def populateTournament(self): #function for adding players from the playerList into the correct games i
        # n the already created tournament
        self.sanitizePlayerList()  # verifies validity of all seeding and gives each player an ID
        playerNumber = len(self.playerList)
        for currentSeed in range(1, playerNumber + 1):  # iterates over all the seeds that are available
            playerWithSeed = None
            gameSeedIndex = None
            seed1Or2 = None
            for currentPlayer in range(playerNumber):  # iterates over all the players in playerList
                if self.playerList[currentPlayer].seed == currentSeed:  # if the player currently being iterated over is the one with the seed we are looking for (currentSeed)
                    playerWithSeed = self.playerList[currentPlayer]  # we save a pointer to that player in playerWithSeed
            for currentGame in range(len(self.rounds[0].games)):
                if self.rounds[0].games[currentGame].seedIndex1 == currentSeed:  # checks if the seed we are iterating over should be placed in this specific game as the higher seeded player
                    gameSeedIndex = currentGame  # if yes, we set a pointer to that game in gameSeedIndex and save that it is the top seed in seed1Or2
                    seed1Or2 = 1
                if self.rounds[0].games[currentGame].seedIndex2 == currentSeed:  # same as above, but checking the lower seed of the game
                    gameSeedIndex = currentGame
                    seed1Or2 = 2
            if seed1Or2 == 1:  # when we find both the player and where they are supposed to go, we check if they are the top or bottom seeded player
                self.rounds[0].games[gameSeedIndex].player1 = playerWithSeed  # if they are top seeded, they go in as player1 in the game for which they are seeded
            elif seed1Or2 == 2:  # otherwise, we they belong to be seeded as player2 in the game for which they are seeded.
                self.rounds[0].games[gameSeedIndex].player2 = playerWithSeed

    def updateTournament(self): #passes over the tournament and updates the bracket (checks for winners and
        # moves winners onto the next game they play)
        roundCounter = 0
        for round in self.rounds:  # loops through every round in the tournament
            for game in round.games:  # loops through every game in the round that is currently being iterated upon
                if int(game.score[0]) > int(game.bestOf) / 2 or game.player2.name == "Null":  # checks if player 1 won the game in question - this is either by having more games than half of the bestOf value or if the other player is a 'Null' player that represents a bye to the next round
                    game.winner = game.player1  # sets the game's winner to the player object that is player1 in this game
                elif int(game.score[1]) > int(game.bestOf) // 2 or game.player1.name == "Null":  # if not player1, it checks if player 2 won and repeats the same as above but for player2
                    game.winner = game.player2
                else:  # if no winners are found, then pass
                    pass

                # after setting the winners in each game, then we move winners onto next games
                if roundCounter != len(self.rounds) - 1:  # this checks whether or not the round we're iterating over is the last round (in which case this algorithm shouldn't run because there's no game to move on to)
                    if game.winner is not None:
                        if round.games.index(game) % 2 == 0:  # the following logic decides where the winner should be moved to. if the game is even in the round.games list, then the player will become player1 in the next game they're progressing to
                            self.rounds[roundCounter + 1].games[int(round.games.index(game) / 2)].player1 = game.winner  # this is the maths for deciding the correct game. For example, the winner of the game of index 0 in round index 0 would move to be player in game index 0 in round index 1
                        if round.games.index(game) % 2 == 1:  # if the game's index is odd in the current round, the winner moves to player2 of the correct game (decided same as above)
                            self.rounds[roundCounter + 1].games[int(round.games.index(game) / 2)].player2 = game.winner

                            roundCounter += 1  # increment the counter

    def setCurrentGame(self, id): #scans the tournament for the game with the id asked for by the parameter and then sets a pointer to it into currentGame
        for round in self.rounds:
            for game in round.games:  # loops over all games in each round in the tournament
                if game.id == id:  # every game's id is compared to the desired id. If the ids match, then the tournament.currentGame is set to that game and the for loop is exited from
                    self.currentGame = game
                    pass

    def setCurrentGameScore(self, score1, score2): #sets the score of the game referred to in currentGame to the desired values
        self.currentGame.score = (score1, score2)

    def setCurrentGameCharacters(self, char1, char2): #sets the characters of the game referred to in currentGame to the desired values
        self.currentGame.player1.currentChar = char1
        self.currentGame.player2.currentChar = char2

    def setCurrentGameBestOf(self, bestOf): #sets the series length of the game referred to in currentGame to the desired values
        self.currentGame.bestOf = bestOf

class PageHandler: #PageHandler object is used to store important pieces of data related to the functioning of the webpage and the flask server.
    active = '' #active refers to which sub-page (i.e. setup, controlpanel or backup) in the interface was selected before sending a request, so that when the redirect to the interface occurs, the same sub-page is selected
    loggedIn = False #stores data whether or not the user is logged in or not
    password = '$2a$12$JhQQvEPl7MwICH6fZYTGVuDLlhjN8n89kPyjcy9V53sFklF66mr5C' #the bcrypt hash of the correct password. This is used to check whether incoming passwords are correct or not
