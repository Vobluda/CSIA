import os
import pickle
import bcrypt

def addIdsToPlayerList(playerList): #this functions adds id's to the current list of players. This is run each time a player is added due to the low computational power required
    idCounter = 1  # when all players have been added, we iterate once more and assign each one a unique id
    for player in playerList: #iterates over the players in playerlist and assigns each one a unique id. These IDs are simply a counter incrementing by 1 each time
        player.id = idCounter
        idCounter += 1

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

def backup(rounds, playerList, fileName): #function used to read the contents of the
    # tournament and back them up in files in /Backups. The rounds and playerList are seperated
    # because of issues that I ran into trying to backup the entire tournament object
    with open(fileName + 'Rounds.backup', 'wb') as openedFile: #opens the file named
        # [fileName]Rounds.backup to be written to in binary
        pickle.dump(rounds, openedFile, protocol=2) #pickles the rounds object of the tournament
        # into the file
    with open(fileName + 'PlayerList.backup', 'wb') as openedFile: #same is done for the
        # playerlist as for the rounds
        pickle.dump(playerList, openedFile, protocol=2)
    print('Backup successful')

def readBackup(tournament, backupName): #function is used to retrieve a backup and set the
    # tournament to the state at which the backup happened
    with open(backupName + 'Rounds.backup', 'rb') as openedFile: #opens the file containing
        # the pickled rounds object based on the backupName
        tournament.rounds = pickle.load(openedFile) #the contents of the pickled file are
        # read into tournament.rounds
    with open(backupName + 'PlayerList.backup', 'rb') as openedFile: #same as above happens
        # for the playerList
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
