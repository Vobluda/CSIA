from flask import Flask, request, render_template, redirect, url_for
from classes import *
import functions

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 #the above are flask config options that are important to running the flask app

tournament = Tournament()
handler = PageHandler()
handler.loggedIn = False
characters = ['Banjo&Kazooie', 'Bayonetta', 'Bowser', 'BowserJr', 'Byleth', 'CaptainFalcon', 'Chrom', 'Cloud', 'Corrin', 'Daisy', 'DarkPit', 'DarkSamus', 'DiddyKong', 'DonkeyKong', 'DrMario', 'DuckHunt', 'Falco', 'Fox', 'Ganondorf', 'Greninja', 'Hero', 'IceClimbers', 'Ike', 'Incineroar', 'Inkling', 'Isabelle', 'Jigglypuff', 'Joker', 'Ken', 'KingDedede', 'KingKRool', 'Kirby', 'Link', 'List.txt', 'LittleMac', 'Lucario', 'Lucas', 'Lucina', 'Luigi', 'Mario', 'Marth', 'MegaMan', 'MetaKnight', 'Mewtwo', 'Mii', 'MinMin', 'MrGame&Watch', 'Ness', 'Olimar', 'Pac-Man', 'Palutena', 'Peach', 'Pichu', 'Pikachu', 'Piranha', 'Pit', 'Pok�monTrainer', 'PyraMythra', 'Richter', 'Ridley', 'ROB', 'Robin', 'Rosalina', 'Roy', 'Ryu', 'Samus', 'Sephiroth', 'Sheik', 'Shulk', 'Simon', 'Snake', 'Sonic', 'Sora', 'Steve', 'Terry', 'ToonLink', 'Villager', 'Wario', 'WiiFitTrainer', 'Wolf', 'Yoshi', 'YoungLink', 'Zelda', 'ZeroSuitSamus']
#the above are certain functions run each time the app is launched. This creates the global variable that references the tournament object and PageHandler object. Finally, there is a global variable holding the list of all characters available to be selected by users

@app.route('/')
def default(): #this function is called whenever no specific path is given. This redirects to the /interface flask call. The redirect is also sent with a 'None' string attached so that the interface knows no sub-page was selected as active
    return redirect('/interface', 'None')

@app.route('/<path:path>')
def getImage(path): #this function is called whenever a path that refers to a static file, this provides the file that is requested
    return app.send_static_file(path)

@app.route('/jsonify')
def jsonify(): #this function is called whenever the OBS app requests the data of tournament. A dict is created from the data in the tournament object
    dict = {'GameId': str(tournament.currentGame.id), 'GamePlayer1': tournament.currentGame.player1.name, 'GamePlayer2': tournament.currentGame.player2.name, 'GameScore1': str(tournament.currentGame.score[0]), 'GameScore2': str(tournament.currentGame.score[1]), 'GamePlayerCharacter1': tournament.currentGame.player1.currentChar, 'GamePlayerCharacter2': tournament.currentGame.player2.currentChar}
    return dict #by returning dict, the flask app translates this into a JSON file, which is sent to the OBS translation app

@app.route('/login', methods=['GET', 'POST'])
def login(): #this function is called whenever the path is /login. The resulting output is dependant on whether or not the GET or POST method is used
    if request.method == 'GET': #if using GET method, then return the template of the login screen. The flag='Unknown' is there for Jinja2 to know not to pop up the error text for the wrong password
        return render_template('LoginTemplate.html', flag='Unknown')
    if request.method == 'POST': #if using POST (which is used when submitting the input form of the password
        if functions.checkPasswords(handler.password, str(request.form['password'])): #if the password is correct (see comments on the function.py file)
            handler.loggedIn = True #set the loggedIn status of the app to True
            return redirect(url_for('interface')) #redirect to the interface, where most of the app is
        else:
            print("Passwords don't match") #if the password is wrong, then output error text into the console and return the same page with the flag 'badPassword'. This tells Jinja2 to pop up the 'wrong password' text
            return render_template('LoginTemplate.html', flag='badPassword')

@app.route('/logout')
def logout(): #this function is called whenever a button links to /logout
    handler.loggedIn = False #sets the app status to logged out and redirects to the login page
    return redirect(url_for('login'))

@app.route('/interface', methods=['GET']) #this page only takes GET requests, because no data submission takes place on this page, but instead on /setup, /controlpanel and /backup
def interface(): #this function is called whenever the page /interface is called. The handler.active is passed so that Jinja2 can change the classes of the navigation buttons based on which sub-page should was selected before refreshing/getting redirected back from form submission
    if handler.loggedIn: #the interface is only returned if the user is logged in, otherwise it redirects to the login page
        return render_template('InterfaceTemplate.html', active=handler.active)
    else:
        return redirect(url_for('login'))

@app.route('/bracket', methods=['GET'])
def bracketPage(): #this function is called whenever the /bracket page is requested (this is called when loading /setup and /controlpanel as an iframe)
    try: #this try except is necessary so that in case there is no tournament bracket created yet no error is returned, but instead the iframe is empty
        return render_template('BracketTemplate.html', tournament=tournament, numRounds=len(tournament.rounds), tournamentTable=functions.formatBracket(tournament)) #the render_template is called on the BracketTemplate Jinja2 template. Several values are passed along which allow the setting of elements on the page based on the current status of the tournament
    except: #if there is an errorthrown, such a nullpointerexception due to the lack of a tournament bracket, then an emtpy html template is sent, which shows up as an empty iframe
        return render_template('Empty.html')

@app.route('/controlPanel', methods=['GET', 'POST'])
def controlPanel(): #this function is called whenever the /controlpanel page is requested. GET and POST return different results, because POST requests to this page are used to submit forms in the /controlpanel sub-page
    if handler.loggedIn: #if the user is not logged in, then return login page
        if request.method == 'GET': #if it's a GET request, then return the controlpanel template with the currentGame and characterList being used to update the page based on the tournament status

            return render_template('ControlPanelTemplate.html', currentGame=tournament.currentGame, characterList=characters)

        if request.method == 'POST': #if the request is a POST request, then check what the form submitted was trying to do

            if request.form['formIdentifier'] == 'changeGame': #I am determining what the request was meant
                # to do based on a hidden value that is changed based on selection using javascript on the page.
                # For example, if the user wants to change the current game, they select it on the site, which
                # changes the formIdentified value to 'changeGame'
                try: #all these functions are wrapped in try except statements to fail gracefully
                    tournament.setCurrentGame(int(request.form['gameID'])) #sets the current game based on the
                    # id input. Check the comments in functions.py for how this works
                except:
                    print('Error occurred while trying to select game')

            elif request.form['formIdentifier'] == 'changeScore': #similar approach is taken for changing all of
                # these, so read the comments for changeGame for more info.
                try:
                    tournament.setCurrentGameScore(request.form['p1Score'], int(request.form['p2Score']))
                except:
                    print('Error occurred while trying to change scores')

                tournament.updateTournament()

            elif request.form['formIdentifier'] == 'changeCharacter':
                try:
                    tournament.setCurrentGameCharacters(request.form['p1Char'], request.form['p2Char'])
                except:
                    print('Error occurred while trying to change characters')

            elif request.form['formIdentifier'] == 'changeBO':
                try:
                    tournament.currentGame.BO = request.form['BO']
                except:
                    print('Error occurred while trying to change series length')

            handler.active = 'controlPanel' #sets the active sub-page to controlpanel so that when it redirects back to /interface the page shows that controlpanel is the active sub-page
            return redirect(url_for('interface')) #redirects to the interface sub-page
    else:
        return redirect(url_for('login'))

@app.route('/setup', methods=['GET', 'POST'])
def setup(): #this function is called whenever the page /setup is requested. Differing results are returned based on GET/POST request. POST request is used for form submission
    if handler.loggedIn: #again, this sub-page only works if the user is logged in
        if request.method == 'GET': #if it's a GET request, then return the setu[ template with the playerlist being used to update the page based on the tournament status

            return render_template('SetupTemplate.html', playerList=tournament.playerList, characterList=characters)

        if request.method == 'POST':

            if request.form['formIdentifier'] == 'addForm': #this is triggered when the user selects they want to add a player.
                if request.form['seed'] == '': #if they have inputted no seed, then the player is made with seed 0 (which will be randomized when the tournament is created)
                    player = Player(request.form['IGN'], request.form['main'], request.form['school'], 0)
                else: #otherwise, make the player object based on the input
                    player = Player(request.form['IGN'], request.form['main'], request.form['school'], request.form['seed'])

                tournament.playerList.append(player) #the player is then appended to the playerlist

            elif request.form['formIdentifier'] == 'editForm': #this is triggered when the user wishes to edit a player's details
                if request.form['ID'] != '':
                    if request.form['seed'] == '': #similar as above, but instead this time the player object inside of the playerlist is changed based on the ID attributed added to them.
                        tournament.playerList[int(request.form['ID']) - 1] = Player(request.form['IGN'], request.form['main'], request.form['school'], 0)
                    else:
                        tournament.playerList[int(request.form['ID']) - 1] = Player(request.form['IGN'], request.form['main'], request.form['school'], request.form['seed'])
                else:
                    print('Player wishing to be edited was not found')

            elif request.form['formIdentifier'] == 'deleteForm': #this is triggered when the user wishes to delete a player from the playerlist
                try:
                    if int(('0' + request.form['ID'])) != 0: #this cast the request.form['ID'] value, which is a string, to an int for the comparison. This if statement checks that the input isn't empty
                        index = 0
                        IDList = []
                        for player in tournament.playerList: #iterates through the playerlist and adds each player's id to the IDList
                            IDList.append(player.id)
                        for ID in IDList: #iterates through the id list, checking if the ID of the player requested to be deleted matches the one currently being iterated over
                            if ID == int(request.form['ID']): #if that is the case, then that player is deleted and the for loop is exited
                                del tournament.playerList[index]
                                pass
                            else: #this is simply here to increment the index counter each time the player is not the one we are looking for
                                index += 1
                except:
                    print('Problem with deleting player')

            elif request.form['formIdentifier'] == 'makeSEBracketForm': #this is triggered when the user finally requests for the tournament bracket to be created
                tournament.resetBracket() #firstly, the tournament's rounds and games are wiped to ensure that previous tournament data doesn't interfere
                tournament.sanitizePlayerList() #then the playerList inputs are sanitized (which validates seeds and creates the appropriate amount of 'Null' players to make the tournament function
                tournament.createTournament() #then, the rounds and games are created
                tournament.populateTournament() #following that, those empty games are populated with the players based on seeding
                tournament.updateTournament() #finally, one pass of updateTournament() is called to ensure that any players seeded against 'Null' players are automatically moved onto the next round
                print("") #finally, the populated bracket is printed into the console for debugging reasons
                functions.printTournament(tournament)
                print("")

            else:
                print('This kind of request is not valid: ' + request.form['formIdentifier']) #if the formIdentifier for some reasons isn't one of the aforementioned values, then an error message is printed in the console
                raise Exception

            handler.active = 'setup' #irregardless of the request, the active value of the handler is set to setup so the interface knows to display that sub-page as the active one
            functions.addIdsToPlayerList(tournament.playerList) #finally, each time something about the playerlist changes (so anytime a POST request is made to /setup), the IDs of the playerlist are updated to match
            return redirect(url_for('interface')) #then, a redirect to /interface occurs
    else:
        return redirect(url_for('login'))

@app.route('/backup', methods=['GET', 'POST'])
def backup(): #this function is called when the /backup page is requested. Again, differing results are returned based on GET/POST request. POST request is used for form submission
    if handler.loggedIn: #this page can only be accessed when logged in
        if request.method == 'GET':

            return render_template('BackupTemplate.html', backupList=functions.generateBackupList()) #when the page is simply requested, the rendered template is returned with the radio menu for selecting backups dynamically updated based on the backups directory

        if request.method == 'POST':

            if request.form['formIdentifier'] == 'backupForm': #if the formIdentifier signifies the user wishes to create a backup
                try:
                    functions.backup(tournament.rounds, tournament.playerList, 'Backups/' + request.form['backupName']) #then then backup function is called and the values from the form are passed into it
                except Exception as e: #because of the manipulation of files, some errors may arise (such as errors with user credentials/access levels on the PC), and so a try except statement is in place to 'fail gracefully'
                    print(e)
                    print("Error occurred while trying to backup tournament")

            if request.form['formIdentifier'] == 'retrieveBackupForm': #if the formIdentifier signifies the user wishes to read a backup
                try:
                    tournament.rounds = functions.readBackup(tournament, 'Backups/' + request.form['backupName']) #then then readBackup function is called and the values from the form are passed into it
                except Exception as e: #again, because of the manipulation of files, some errors may arise (such as errors with user credentials/access levels on the PC), and so a try except statement is in place to 'fail gracefully'
                    print(e)
                    print("Error occurred while trying to return to backup of tournament")

            handler.active = 'backup' #the handler.active is set to 'backup' so /interface knows to display it as the active sub-page
            return redirect(url_for('interface')) #then the user is redirected back to interface
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(ssl_context='adhoc')
