import json

from flask import Flask, request, render_template, redirect, url_for

import functions
from classes import *

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

tournament = Tournament()
handler = PageHandler()
handler.loggedIn = False
characters = ['Banjo&Kazooie', 'Bayonetta', 'Bowser', 'BowserJr', 'Byleth', 'CaptainFalcon', 'Chrom', 'Cloud', 'Corrin', 'Daisy', 'DarkPit', 'DarkSamus', 'DiddyKong', 'DonkeyKong', 'DrMario', 'DuckHunt', 'Falco', 'Fox', 'Ganondorf', 'Greninja', 'Hero', 'IceClimbers', 'Ike', 'Incineroar', 'Inkling', 'Isabelle', 'Jigglypuff', 'Joker', 'Ken', 'KingDedede', 'KingKRool', 'Kirby', 'Link', 'List.txt', 'LittleMac', 'Lucario', 'Lucas', 'Lucina', 'Luigi', 'Mario', 'Marth', 'MegaMan', 'MetaKnight', 'Mewtwo', 'Mii', 'MinMin', 'MrGame&Watch', 'Ness', 'Olimar', 'Pac-Man', 'Palutena', 'Peach', 'Pichu', 'Pikachu', 'Piranha', 'Pit', 'Pok�monTrainer', 'PyraMythra', 'Richter', 'Ridley', 'ROB', 'Robin', 'Rosalina', 'Roy', 'Ryu', 'Samus', 'Sephiroth', 'Sheik', 'Shulk', 'Simon', 'Snake', 'Sonic', 'Sora', 'Steve', 'Terry', 'ToonLink', 'Villager', 'Wario', 'WiiFitTrainer', 'Wolf', 'Yoshi', 'YoungLink', 'Zelda', 'ZeroSuitSamus']

@app.route('/')
def default():
    return redirect('/interface', 'None')

@app.route('/<path:path>')
def getImage(path):
    return app.send_static_file(path)

@app.route('/jsonify')
def jsonify():
    dict = {'GameId': str(tournament.currentGame.id), 'GamePlayer1': tournament.currentGame.player1.name, 'GamePlayer2': tournament.currentGame.player2.name, 'GameScore1': str(tournament.currentGame.score[0]), 'GameScore2': str(tournament.currentGame.score[1]), 'GamePlayerCharacter1': tournament.currentGame.player1.currentChar, 'GamePlayerCharacter2': tournament.currentGame.player2.currentChar}
    return dict

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('LoginTemplate.html', flag='Unknown')
    if request.method == 'POST':
        if functions.checkPasswords(handler.password, str(request.form['password'])):
            handler.loggedIn = True
            return redirect(url_for('interface'))
        else:
            print("Passwords don't match")
            return render_template('LoginTemplate.html', flag='badPassword')

@app.route('/logout')
def logout():
    handler.loggedIn = False
    return redirect(url_for('login'))

@app.route('/interface')
def interface():
    if handler.loggedIn:
        return render_template('InterfaceTemplate.html', active=handler.active)
    else:
        return redirect(url_for('login'))

@app.route('/bracket', methods=['GET'])
def bracketPage():
    try:
        return render_template('BracketTemplate.html', tournament=tournament, numRounds=len(tournament.rounds), tournamentTable=functions.formatBracket(tournament))
    except Exception as e:
        print(e)
        return render_template('Empty.html')

@app.route('/controlPanel', methods=['GET', 'POST'])
def controlPanel():
    if handler.loggedIn:
        if request.method == 'GET':
            return render_template('ControlPanelTemplate.html', currentGame=tournament.currentGame, characterList=characters)
        if request.method == 'POST':

            if request.form['formIdentifier'] == 'changeGame':
                try:
                    tournament.setCurrentGame(int(request.form['gameID']))
                except:
                    print('Error occurred while trying to select game')

            if request.form['formIdentifier'] == 'changeScore':
                try:
                    tournament.setCurrentGameScore(request.form['p1Score'], int(request.form['p2Score']))
                except:
                    print('Error occurred while trying to change scores')

                tournament.updateTournament()

            if request.form['formIdentifier'] == 'changeCharacter':
                try:
                    tournament.setCurrentGameCharacters(request.form['p1Char'], request.form['p2Char'])
                except:
                    print('Error occurred while trying to change characters')

            if request.form['formIdentifier'] == 'changeBO':
                try:
                    tournament.currentGame.BO = request.form['BO']
                except:
                    print('Error occurred while trying to change series length')

            handler.active = 'controlPanel'
            return redirect(url_for('interface'))
    else:
        return redirect(url_for('login'))

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if handler.loggedIn:
        if request.method == 'GET':
            return render_template('SetupTemplate.html', playerList=tournament.playerList, characterList=characters)
        if request.method == 'POST':

            if request.form['formIdentifier'] == 'addForm':
                if request.form['seed'] == '':
                    player = Player(request.form['IGN'], request.form['main'], request.form['school'], 0)
                else:
                    player = Player(request.form['IGN'], request.form['main'], request.form['school'], request.form['seed'])

                tournament.playerList.append(player)

            elif request.form['formIdentifier'] == 'editForm':
                if request.form['ID'] != '':
                    if request.form['seed'] == '':
                        tournament.playerList[int(request.form['ID']) - 1] = Player(request.form['IGN'], request.form['main'], request.form['school'], 0)
                    else:
                        tournament.playerList[int(request.form['ID']) - 1] = Player(request.form['IGN'], request.form['main'], request.form['school'], request.form['seed'])
                else:
                    print('Player wishing to be edited was not found')

            elif request.form['formIdentifier'] == 'deleteForm':
                if int(('0' + request.form['ID'])) != 0:
                    index = 0
                    IDList = []
                    for player in tournament.playerList:
                        IDList.append(player.id)
                    for ID in IDList:
                        if ID == int(request.form['ID']):
                            delete = tournament.playerList.pop(index)
                            pass
                        else:
                            index = index + 1
                elif request.form['IGN'] != '':
                    try:
                        i = 0
                        for i in range(0, len(tournament.playerList)):
                            if (tournament.playerList[i].name == request.form['IGN']):
                                index = i
                            else:
                                i += 1
                        del tournament.playerList[index]
                    except:
                        print("Couldn't find player")

            elif request.form['formIdentifier'] == 'makeSEBracketForm':
                tournament.resetBracket()
                functions.sanitizePlayerList(tournament.playerList)
                tournament.createTournament()
                tournament.populateTournament()
                tournament.updateTournament()
                print("")
                functions.printTournament(tournament)
                print("")

            else:
                print('This kind of request is not valid: ' + request.form['formIdentifier'])
                raise Exception

            handler.active = 'setup'
            functions.addIdsToPlayerList(tournament.playerList)
            return redirect(url_for('interface'))
    else:
        return redirect(url_for('login'))

@app.route('/backup', methods=['GET', 'Post'])
def backup():
    if handler.loggedIn:
        if request.method == 'GET':
            return render_template('BackupTemplate.html', backupList=functions.generateBackupList())

        if request.method == 'POST':

            if request.form['formIdentifier'] == 'backupForm':
                try:
                    functions.backup(tournament.rounds, tournament.playerList, 'Backups/' + request.form['backupName'])
                except Exception as e:
                    print(e)
                    print("Error occurred while trying to backup tournament")

            if request.form['formIdentifier'] == 'retrieveBackupForm':
                try:
                    tournament.rounds = functions.readBackup(tournament, 'Backups/' + request.form['backupName'])
                except Exception as e:
                    print(e)
                    print("Error occurred while trying to return to backup of tournament")

            handler.active = 'backup'
            return redirect(url_for('interface'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
