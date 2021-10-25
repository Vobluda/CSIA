from flask import Flask, request, render_template, redirect

import functions
from classes import *
from functions import formatBracket

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

tournament = Tournament()

@app.route('/')
def default():
    return redirect('/controlPanel')

@app.route('/<path:path>')
def getImage(path):
    return app.send_static_file(path)

@app.route('/interface')
def interface():
    return render_template('InterfaceTemplate.html')

@app.route('/bracket', methods=['GET'])
def bracketPage():
    try:
        return render_template('BracketTemplate.html', tournament=tournament, numRounds=len(tournament.rounds), tournamentTable=formatBracket(tournament))
    except Exception as e:
        print(e)
        return render_template('Empty.html')

@app.route('/controlPanel', methods=['GET', 'POST'])
def controlPanel():
    if request.method == 'GET':
        return render_template('ControlPanelTemplate.html', currentGame=tournament.currentGame)
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

        return render_template('ControlPanelTemplate.html', currentGame=tournament.currentGame)

@app.route('/setup', methods=['GET', 'POST'])
def setup():
    if request.method == 'GET':
        return render_template('SetupTemplate.html', playerList=tournament.playerList)
    if request.method == 'POST':

        if request.form['formIdentifier'] == 'addForm':
            if request.form['seed'] == '':
                player = Player(request.form['IGN'], request.form['main'], request.form['school'], 0)
            else:
                player = Player(request.form['IGN'], request.form['main'], request.form['school'], request.form['seed'])

            tournament.playerList.append(player)

        elif request.form['formIdentifier'] == 'editForm':
            if request.form['seed'] == '':
                 tournament.playerList[int(request.form['ID']) - 1] = Player(request.form['IGN'], request.form['main'], request.form['school'], 0)
            else:
                tournament.playerList[int(request.form['ID']) - 1] = Player(request.form['IGN'], request.form['main'], request.form['school'], request.form['seed'])

        elif request.form['formIdentifier'] == 'deleteForm':
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

        elif request.form['formIdentifier'] == 'backupForm':
            try:
                functions.backup(tournament, 'Backups/' + request.form['backupName'])
            except Exception as e:
                print(e)
                print("Error occurred while trying to backup tournament")

        elif request.form['formIdentifier'] == 'retrieveBackupForm':
            functions.readBackup('Backups/')
            tournament.ID = len(tournament.playerList) + 1

        elif request.form['formIdentifier'] == 'makeSEBracketForm':
            tournament.resetBracket()
            tournament.createTournament()
            tournament.populateTournament()
            print("")
            functions.printTournament(tournament)
            print("")

        else:
            print('This kind of request is not valid: ' + request.form['formIdentifier'])
            raise Exception

        return render_template('SetupTemplate.html', playerList=tournament.playerList)

@app.route('/backup', methods=['GET', 'Post'])
def backup():
    if request.method == 'GET':
        return render_template('BackupTemplate.html', backupList=functions.generateBackupList())

    if request.method == 'POST':

        if request.form['formIdentifier'] == 'backupForm':
            try:
                functions.backup(tournament, 'Backups/' + request.form['backupName'])
            except Exception as e:
                print(e)
                print("Error occurred while trying to backup tournament")

        if request.form['formIdentifier'] == 'retrieveBackupTournamentForm':
            try:
                functions.readBackup('Backups/' + request.form['backupName'])
            except Exception as e:
                print(e)
                print("Error occurred while trying to return to backup of tournament")

        return render_template('BackupTemplate.html', backupList=functions.generateBackupList())

if __name__ == '__main__':
    app.run()
