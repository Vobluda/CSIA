import math
import os
import pickle
import random

import bcrypt

from classes import *

def resetBracket(tournament): #function that takes a tournament object and clears the games and rounds list so that a new tournament bracket can be created without problems
    if tournament.rounds is not None: #as long as the tournaments isn't empty
        tournament.rounds.clear() #removes all the round objects in the tournament
    tournament.rounds = [] #it then resets tournament.rounds to a list, because .clear() doesn't leave a list behind, but instead Null

def createEmptyTournament(tournament): #function that creates an empty bracket (i.e. populates the tournament object with rounds and games, but without adding in the players)
    playerList = tournament.playerList
    roundNumber = int(math.ceil(math.log(len(playerList), 2)))  #find the lowest possible round number (log base 2 of the amount of players rounded up)
    for currentRound in range(0, roundNumber):  #loop over the round indices
        tournament.rounds.append(Round())  #appends a new round object to the rounds list
        if currentRound == 0:  #if the current round is the first one created
            tournament.rounds[currentRound].games = [Game(1, 2)]  #add the final game (seeing as the bracket is created backwards)
        else:
            for currentGame in range(int(2 ** currentRound)):  #iterates over the necessary amount of games per round (number of games is derived by the round number)
                if currentGame % 2 == 0:  #if the game number is even
                    seedIndex1 = tournament.rounds[currentRound - 1].games[currentGame // 2].seedIndex1  #the seedindex1 for this game is derived from the previous games' seedindex1
                else:
                    seedIndex1 = tournament.rounds[currentRound - 1].games[currentGame // 2].seedIndex2  #if the game is odd, the seedindex1 for this game is derived from the previous games' seedindex2
                seedIndex2 = int(2 ** (currentRound + 1)) + 1 - seedIndex1  #the other seed index is derived as the opposite of the seeding of the seedindex1 (so if seedindex1 is the 1st seed in a round with 8 players, seedindex2 would be the 8th seed)
                tournament.rounds[currentRound].games.append(Game(seedIndex1, seedIndex2))  #adds this created game to the respective round it belongs to
    tournament.rounds = tournament.rounds[::-1]  #after all games and rounds have been created, the round order is flipped to create the conventional bracket structure
    gameIDCounter = 0
    for curr_round in tournament.rounds:  #iterates over all games and gives each game a unique id
        for curr_game in curr_round.games:
            gameIDCounter += 1
            curr_game.id = gameIDCounter

def populateEmptyTournament(tournament):
    sanitizePlayerList(tournament.playerList) #verifies validity of all seeding and gives each player an ID
    playerNumber = len(tournament.playerList)
    for currentSeed in range(1, playerNumber + 1): #iterates over all the seeds that are available
        playerWithSeed = None
        gameSeedIndex = None
        seed1Or2 = None
        for currentPlayer in range(playerNumber): #iterates over all the players in playerList
            if tournament.playerList[currentPlayer].seed == currentSeed: #if the player currently being iterated over is the one with the seed we are looking for (currentSeed)
                playerWithSeed = tournament.playerList[currentPlayer] #we save a pointer to that player in playerWithSeed
        for currentGame in range(len(tournament.rounds[0].games)):
            if tournament.rounds[0].games[currentGame].seedIndex1 == currentSeed: #checks if the seed we are iterating over should be placed in this specific game as the higher seeded player
                gameSeedIndex = currentGame #if yes, we set a pointer to that game in gameSeedIndex and save that it is the top seed in seed1Or2
                seed1Or2 = 1
            if tournament.rounds[0].games[currentGame].seedIndex2 == currentSeed: #same as above, but checking the lower seed of the game
                gameSeedIndex = currentGame
                seed1Or2 = 2
        if seed1Or2 == 1: #when we find both the player and where they are supposed to go, we check if they are the top or bottom seeded player
            tournament.rounds[0].games[gameSeedIndex].player1 = playerWithSeed #if they are top seeded, they go in as player1 in the game for which they are seeded
        elif seed1Or2 == 2: #otherwise, we they belong to be seeded as player2 in the game for which they are seeded.
            tournament.rounds[0].games[gameSeedIndex].player2 = playerWithSeed

def updateTournament(tournament): #function that takes the tournament, checks for any winners or byes and moves the winners onto the correct game in the next round
    roundCounter = 0
    for round in tournament.rounds: #loops through every round in the tournament
        for game in round.games: #loops through every game in the round that is currently being iterated upon
            if int(game.score[0]) > int(game.bestOf) / 2 or game.player2.name == "Null": #checks if player 1 won the game in question - this is either by having more games than half of the bestOf value or if the other player is a 'Null' player that represents a bye to the next round
                game.winner = game.player1 #sets the game's winner to the player object that is player1 in this game
            elif int(game.score[1]) > int(game.bestOf) // 2 or game.player1.name == "Null": #if not player1, it checks if player 2 won and repeats the same as above but for player2
                game.winner = game.player2
            else: #if no winners are found, then pass
                pass

            #after setting the winners in each game, then we move winners onto next games
            if roundCounter != len(tournament.rounds) - 1: #this checks whether or not the round we're iterating over is the last round (in which case this algorithm shouldn't run because there's no game to move on to)
                if game.winner is not None:
                    if round.games.index(game) % 2 == 0: #the following logic decides where the winner should be moved to. if the game is even in the round.games list, then the player will become player1 in the next game they're progressing to
                        tournament.rounds[roundCounter + 1].games[int(round.games.index(game) / 2)].player1 = game.winner #this is the maths for deciding the correct game. For example, the winner of the game of index 0 in round index 0 would move to be player in game index 0 in round index 1
                    if round.games.index(game) % 2 == 1: #if the game's index is odd in the current round, the winner moves to player2 of the correct game (decided same as above)
                        tournament.rounds[roundCounter + 1].games[int(round.games.index(game) / 2)].player2 = game.winner

        roundCounter += 1 #increment the counter

def addIdsToPlayerList(playerList): #this functions adds id's to the current list of players. This is run each time a player is added due to the low computational power required
    idCounter = 1  # when all players have been added, we iterate once more and assign each one a unique id
    for player in playerList: #iterates over the players in playerlist and assigns each one a unique id. These IDs are simply a counter incrementing by 1 each time
        player.id = idCounter
        idCounter += 1

def sanitizePlayerList(playerList): #this function is used to 'sanitize' the user input into the playerlist (such as invalid seeding or not enough players to make a tournament)

    i = 0 #the following chunk of code is used to remove any 'Null' players that represent byes. These are removed because if a tournament is created on top of an already existing tournament (i.e. to update seeding etc.) the 'Null' players still remain, causing problems
    while i < len(playerList): #iterates over playerList and if any player has a name 'Null' they are removed
        if playerList[i].name == 'Null':
            del playerList[i]
        else:
            i += 1

    takenSeeds = [] #creates a list that will store all seeds being used already
    for player in playerList: #iterates over every player in the playerlist
        player.seed = int(player.seed)
        if player.seed is None: #the following will set the seed to 0 (to be changed in the future) if the seed is None, already taken by a previous player or not a valid seed (i.e. below 0 or over the amount players in the playerList)
            player.seed = 0
        elif player.seed in takenSeeds:
            player.seed = 0
        elif player.seed <= 0 or player.seed > len(playerList):
            player.seed = 0
        else: takenSeeds.append(player.seed) #if a player's seed satisfies the above, their seed is added to the list of already taken seeds so further players can't use it

    availableSeeds = [] #based on the list of already taken seeds, another list containing valid seeds that are not being used is created
    for i in range (1, len(playerList)+1):
        if i not in takenSeeds:
            availableSeeds.append(i)

    random.shuffle(availableSeeds) #these available seeds are shuffled (i.e. random order) so that there is no bias towards early entries when randomly seeding.

    for player in playerList: #iterates over the playerlist and any players with a seed of 0 (from before) are now given a random available seed
        if player.seed == 0:
            player.seed = availableSeeds[0]
            del availableSeeds[0]

    seedCounter = 1 #the following adds the remaining 'null' players that represent an automatic win to the next round (necessary as each bracket needs a power of 2 amount of players)
    while math.log2(len(playerList)) != math.floor(math.log2(len(playerList))): #while the amount of players in the playerlist is not an exponent of 2
        playerList.append(Player("Null", "", "", len(playerList)+seedCounter)) #creates a 'null' character, which can later be checked for as an automatic win
        seedCounter += 1

    addIdsToPlayerList(playerList) #finally, it adds ids to the players again so that 'Null' players are also given ids


def setCurrentGame(tournament, id): #this function sets the tournament.currentGame to a game specificied based on id
    for round in tournament.rounds:
        for game in round.games: #loops over all games in each round in the tournament
            if game.id == id: #every game's id is compared to the desired id. If the ids match, then the tournament.currentGame is set to that game and the for loop is exited from
                tournament.currentGame = game
                pass

def setCurrentGameScore(tournament, score1, score2): #this function is used to set the score of the current game
    tournament.currentGame.score = (score1, score2)

def setCurrentGameCharacter(tournament, char1, char2): #this function used to set the characters in the currentGame (note it does not update defaultChar, because that is persisten across games)
    tournament.currentGame.player1.currentChar = char1
    tournament.currentGame.player2.currentChar = char2

def setCurrentGameBestOf(tournament, bestOf): #this function is used to set the bestOf of the currentGame (i.e. this dictates how many points are needed to win before being deemed the winner of the game)
    tournament.currentGame.bestOf = bestOf

def formatBracket(tournament): #this function is used to format the tournament object in such a way that a 2D list is returned which is used to construct the visualisation of the bracket in the interface
    roundNumber = len(tournament.rounds)
    gameNumber = int(2 ** roundNumber) - 1
    tableList = [["" for j in range(roundNumber)] for i in range(gameNumber)] #this is used to create the 2D list into which the bracket will be filled into. I have used one line for loops to minimise line count
    prespace = 0
    midspace = 1 #these values dictate the amount of space between rounds and games in the table, but these are changed as the rounds are iterated over
    for currentCol in range(roundNumber): #iterates over the columns in the 2D list
        gameCounter = 0
        for currentRow in range(gameNumber): #iterates over the rows in the table
            if currentRow == prespace + (gameCounter * (midspace + 1)): #if the specific space in the 2D list being iterated over right now is meant to hold a game, then:
                tableList[currentRow][currentCol] = tournament.rounds[currentCol].games[gameCounter] #fill up the specific 'cell' in the 2D list currently pointed to with the corresponding game (as dictated by gameCounter)
                gameCounter += 1 #increment gameCounter by 1
        prespace = (prespace * 2) + 1
        midspace = (midspace * 2) + 1 #adjust the prespace and midspace to make the formatting of the table work out
    return tableList #returns the 2D list to be passed to Jinja2 for visualisation

def printTournament(tournament): #function that is used to print a formatted output of the tournament bracket into the console. Mainly used for debugging
    txt = "Game ID: {id}, Player 1: {p1}, Player 2: {p2}, seedIndex1: {s1}, seedIndex2: {s2}" #this is the template for the game, where the placeholders are changed each game
    roundCounter = 1
    print("===Tournament===")
    for round in tournament.rounds: #iterates over the rounds
        print("Round " + str(roundCounter)) #print which round is being printed
        for game in round.games: #iterates over the games in that round and prints key details about each game
            print(txt.format(id = game.id, p1 = game.player1.name, p2 = game.player2.name, s1 = game.seedIndex1, s2 = game.seedIndex2))
        roundCounter += 1 #increments roundCounter by 1

def printPlayerList(playerList): #function that is used to print a formatted output of the player list into the console. Mainly used for debugging
    txt = "Name: {name}, ID: {id}, Seed: {seed}" #string used as a format, with placeholders replaced with each print
    for player in playerList: #iterates over the players in playerList
        print(txt.format(name = player.name, id = player.id, seed = player.seed)) #print out a string outlining key details of each player

def backup(rounds, playerList, fileName): #function used to read the contents of the tournament and back them up in files in /Backups. The rounds and playerList are seperated because of issues that I ran into trying to backup the entire tournament object
    with open(fileName + 'Rounds.backup', 'wb') as openedFile: #opens the file named [fileName]Rounds.backup to be written to in binary
        pickle.dump(rounds, openedFile, protocol=2) #pickles the rounds object of the tournament into the file
    with open(fileName + 'PlayerList.backup', 'wb') as openedFile: #same is done for the playerlist as for the rounds
        pickle.dump(playerList, openedFile, protocol=2)
    print('Backup successful')

def readBackup(tournament, backupName): #function is used to retrieve a backup and set the tournament to the state at which the backup happened
    with open(backupName + 'Rounds.backup', 'rb') as openedFile: #opens the file containing the pickled rounds object based on the backupName
        tournament.rounds = pickle.load(openedFile) #the contents of the pickled file are read into tournament.rounds
    with open(backupName + 'PlayerList.backup', 'rb') as openedFile: #same as above happens for the playerList
        tournament.playerList = pickle.load(openedFile)
    print('Backup retrieved successfully')

def generateBackupList(): #this function is used to generate the list of backups, which are passed onto Jinja2 when making the backups page so that users can choose from a radio menu on the page
    backups = []
    for filename in os.listdir('Backups'): #iterates over the filenames in the /Backups directory
        if 'Rounds' in filename: #if the current filename refers to a backup of rounds
            if filename.replace('Rounds.backup', '') not in backups: #and the name of the backup without 'Rounds' is not already in the list
                backups.append(filename.replace('Rounds.backup', '')) #then add the filename (without 'Rounds') into the list
        elif 'PlayerList' in filename: #same is run for backups of playerLists just in case, but if everything goes correctly then all these filenames should already be in the list
            if filename.replace('PlayerList.backup', '') not in backups:
                backups.append(filename.replace('PlayerList.backup', ''))
    return backups #returns the list of backup names to populate the selection on the page

def checkPasswords(hash, password): #function is used for checking if the incoming password matches the correct password (given there is a universal password because there is no distinction is access levels)
    if bcrypt.hashpw(str(password).encode('utf-8'), hash.encode('utf-8')) == hash.encode('utf-8'): #using the bcrypt library, it compares the bcrypt hashes of the password string and the hash of the correct password. This is done because I have opted to not store the plaintext correct password in the python files for security reasons, instead only storing the hash of the password.
        return True #if the passwords match, then return true. If not, return false
    else:
        return False
