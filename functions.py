import math
import os
import pickle
import random

import bcrypt

from classes import *

def resetBracket(tournament):
    if tournament.rounds is not None:
        for round in tournament.rounds:
            round.games.clear()
        tournament.rounds.clear()

    tournament.rounds = []

def createEmptyTournament(tournament):
    playerList = tournament.playerList
    roundNumber = int(math.ceil(math.log(len(playerList), 2)))  # find the lowest possible round number (log base 2 of the amount of players rounded up)
    for currentRound in range(0, roundNumber):  # loop over the round indices
        tournament.rounds.append(Round())  # appends a new round object to the rounds list
        if currentRound == 0:  # if the current round is the first one created
            tournament.rounds[currentRound].games = [Game(1, 2)]  # add the final game (seeing as the bracket is created backwards)
        else:
            for currentGame in range(int(2 ** currentRound)):  # iterates over the necessary amount of games per round (number of games is derived by the round number)
                if currentGame % 2 == 0:  # if the game number is even
                    seedIndex1 = tournament.rounds[currentRound - 1].games[currentGame // 2].seedIndex1  # the seedindex1 for this game is derived from the previous games' seedindex1
                else:
                    seedIndex1 = tournament.rounds[currentRound - 1].games[currentGame // 2].seedIndex2  # if the game is odd, the seedindex1 for this game is derived from the previous games' seedindex2
                seedIndex2 = int(2 ** (currentRound + 1)) + 1 - seedIndex1  # the other seed index is derived as the opposite of the seeding of the seedindex1 (so if seedindex1 is the 1st seed in a round with 8 players, seedindex2 would be the 8th seed)
                tournament.rounds[currentRound].games.append(Game(seedIndex1, seedIndex2))  # adds this created game to the respective round it belongs to
    tournament.rounds = tournament.rounds[::-1]  # after all games and rounds have been created, the round order is flipped to create the conventional bracket structure
    gameIDCounter = 0
    for curr_round in tournament.rounds:  # iterates over all games and gives each game a unique id
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

def updateTournament(tournament):
    roundCounter = 0
    for round in tournament.rounds:
        for game in round.games:
            if int(game.score[0]) > int(game.bestOf) / 2 or game.player2.name == "Null":
                game.winner = game.player1
            elif int(game.score[1]) > int(game.bestOf) // 2 or game.player1.name == "Null":
                game.winner = game.player2
            else:
                pass
            # move winners onto next games
            if roundCounter != len(tournament.rounds) - 1:
                if game.winner is not None:
                    if round.games.index(game) % 2 == 0:
                        tournament.rounds[roundCounter + 1].games[int(round.games.index(game) / 2)].player1 = game.winner
                    if round.games.index(game) % 2 == 1:
                        tournament.rounds[roundCounter + 1].games[int(round.games.index(game) / 2)].player2 = game.winner

        roundCounter = roundCounter + 1

def addIdsToPlayerList(playerList):
    idCounter = 1  # when all players have been added, we iterate once more and assign each one a unique id
    for player in playerList:
        player.id = idCounter
        idCounter += 1

def sanitizePlayerList(playerList):

    i = 0
    while i < len(playerList):
        if playerList[i].name == 'Null':
            del playerList[i]
        else:
            i += 1

    takenSeeds = [] #creates a list that will store all seeds being used already
    for player in playerList: #iterates over every player in the playerlist
        player.seed = int(player.seed)
        if player.seed is None: #the following will set the seed to 0 (to be changed in the future) if the seed is None, already taken by a previous player or not a valid seed
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

    random.shuffle(availableSeeds)

    for player in playerList: #iterates over the playerlist and any players with a seed of 0 (from before) are now given a random available seed
        if player.seed == 0:
            player.seed = availableSeeds[0]
            del availableSeeds[0]

    seedCounter = 1 #the following adds the remaining 'null' players that represent an automatic win to the next round (necessary as each bracket needs a power of 2 amount of players)
    while math.log2(len(playerList)) != math.floor(math.log2(len(playerList))): #while the amount of players in the playerlist is not an exponent of 2
        playerList.append(Player("Null", "", "", len(playerList)+seedCounter)) #creates a 'null' character, which can later be checked for as an automatic win
        seedCounter += 1

    addIdsToPlayerList(playerList)


def setCurrentGame(tournament, id):
    for round in tournament.rounds:
        for game in round.games:
            if game.id == id:
                tournament.currentGame = game
                pass

def setCurrentGameScore(tournament, score1, score2):
    tournament.currentGame.score = (score1, score2)

def setCurrentGameCharacter(tournament, char1, char2):
    tournament.currentGame.player1.currentChar = char1
    tournament.currentGame.player2.currentChar = char2

def setCurrentGameBestOf(tournament, bestOf):
    tournament.currentGame.bestOf = bestOf

def formatBracket(tournament):
    roundNumber = len(tournament.rounds)
    gameNumber = int(2 ** roundNumber) - 1
    tableList = [["" for j in range(roundNumber)] for i in range(gameNumber)]
    prespace = 0
    midspace = 1
    for currentCol in range(roundNumber):
        gameCounter = 0
        for current_row in range(gameNumber):
            if current_row == prespace + (gameCounter * (midspace + 1)):
                tableList[current_row][currentCol] = tournament.rounds[currentCol].games[gameCounter]
                gameCounter += 1
        prespace = (prespace * 2) + 1
        midspace = (midspace * 2) + 1
    return tableList

def printTournament(tournament):
    txt = "Game ID: {id}, Player 1: {p1}, Player 2: {p2}, seedIndex1: {s1}, seedIndex2: {s2}"
    roundCounter = 1
    print("===Tournament===")
    for round in tournament.rounds:
        print("Round " + str(roundCounter))
        for game in round.games:
            print(txt.format(id = game.id, p1 = game.player1.name, p2 = game.player2.name, s1 = game.seedIndex1, s2 = game.seedIndex2))
        roundCounter += 1

def printPlayerList(playerList):
    txt = "Name: {name}, ID: {id}, Seed: {seed}"
    for player in playerList:
        print(txt.format(name = player.name, id = player.id, seed = player.seed))

def backup(rounds, playerList, fileName):
    with open(fileName + 'Rounds.backup', 'wb') as openedFile:
        pickle.dump(rounds, openedFile, protocol=2)
    with open(fileName + 'PlayerList.backup', 'wb') as openedFile:
        pickle.dump(playerList, openedFile, protocol=2)
    print('Backup successful')

def readBackup(tournament, backupName):
    with open(backupName + 'Rounds.backup', 'rb') as openedFile:
        tournament.rounds = pickle.load(openedFile)
    with open(backupName + 'PlayerList.backup', 'rb') as openedFile:
        tournament.playerList = pickle.load(openedFile)
    print('Backup retrieved successfully')

def generateBackupList():
    backups = []
    for filename in os.listdir('Backups'):
        if 'Rounds' in filename:
            if filename.replace('Rounds.backup', '') not in backups:
                backups.append(filename.replace('Rounds.backup', ''))
        if 'PlayerList' in filename:
            if filename.replace('PlayerList.backup', '') not in backups:
                backups.append(filename.replace('PlayerList.backup', ''))
    return backups

def checkPasswords(hash, password):
    if bcrypt.hashpw(str(password).encode('utf-8'), hash.encode('utf-8')) == hash.encode('utf-8'):
        return True
    else:
        return False
