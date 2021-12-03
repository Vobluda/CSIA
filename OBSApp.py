import shutil
import time
import requests
import json
import os

ip = input("Input the ip address/url of the server: ") # I need to know where to request the data from
directory = input("Input the directory location for where to save the txt files: ") #And where to save the .txt files to

while True: #This process runs consistently as a polling-based app, with 5 second intervals between polls

    try: #Try-Except statement to 'fail gracefully'
        r = requests.get('http://' + ip + '/jsonify') #Using the python requests library to request from the desired IP
        result = r.json() #the request's response is written as a dict to results (JSON is just a fancy dictionary)

        with open(directory + '/GameId.txt', 'w') as f: #Go through each value and write to the correct .txt file
            f.write(result["GameId"])

        with open(directory + '/GamePlayer1.txt', 'w') as f:
            f.write(result["GamePlayer1"])

        with open(directory + '/GamePlayer2.txt', 'w') as f:
            f.write(result["GamePlayer2"])

        with open(directory + '/GameScore1.txt', 'w') as f:
            f.write(result["GameScore1"])

        with open(directory + '/GameScore2.txt', 'w') as f:
            f.write(result["GameScore2"])

        if result["GamePlayerCharacter1"] != '': #Characters need a bit more work because I need to send a .png file
            char1Request = requests.get('http://' + ip + '/static/' + result["GamePlayerCharacter1"] + '.png', stream=True)
            with open(directory + '/GamePlayerCharacter1.png', 'wb') as f: #The image is requested from the server and
                shutil.copyfileobj(char1Request.raw, f) #the raw binary is written to the correct file

        if result["GamePlayerCharacter2"] != '':
            char2Request = requests.get('http://' + ip + '/static/' + result["GamePlayerCharacter2"] + '.png', stream=True)
            with open(directory + '/GamePlayerCharacter2.png', 'wb') as f:
                shutil.copyfileobj(char2Request.raw, f)

    except Exception as e:
        print(e)
        pass

    time.sleep(5)
