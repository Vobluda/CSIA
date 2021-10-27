import shutil
import time
import requests
import json
import os

ip = input("Input the ip address/url of the server: ")
directory = input("Input the directory location for where to save the txt files: ")

while True:

    try:
        r = requests.get('http://' + ip + '/jsonify')
        result = r.json()

        with open(directory + '/GameId.txt', 'w') as f:
            f.write(result["GameId"])

        with open(directory + '/GamePlayer1.txt', 'w') as f:
            f.write(result["GamePlayer1"])

        with open(directory + '/GamePlayer2.txt', 'w') as f:
            f.write(result["GamePlayer2"])

        with open(directory + '/GameScore1.txt', 'w') as f:
            f.write(result["GameScore1"])

        with open(directory + '/GameScore2.txt', 'w') as f:
            f.write(result["GameScore2"])

        if result["GamePlayerCharacter1"] != '':
            char1Request = requests.get('http://' + ip + '/static/' + result["GamePlayerCharacter1"] + '.png', stream=True)
            with open(directory + '/GamePlayerCharacter1.png', 'wb') as f:
                shutil.copyfileobj(char1Request.raw, f)

        if result["GamePlayerCharacter2"] != '':
            char2Request = requests.get('http://' + ip + '/static/' + result["GamePlayerCharacter2"] + '.png', stream=True)
            with open(directory + '/GamePlayerCharacter2.png', 'wb') as f:
                shutil.copyfileobj(char2Request.raw, f)

    except Exception as e:
        print(e)
        pass

    time.sleep(5)
