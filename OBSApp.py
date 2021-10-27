import time
import requests
import json
import os

ip = input("Input the ip address/url of the server: ")
directory = input("Input the directory location for where to save the txt files: ")

while True:

    r = requests.get(ip + '/jsonify')
    result = r.json()
    parsedResult = json.load(result)

    with open(dir + '/GameId.txt', 'w') as f:
        f.write(parsedResult["GameId"])

    with open(dir + '/GamePlayer1.txt', 'w') as f:
        f.write(parsedResult["GamePlayer1"])

    with open(dir + '/GamePlayer2.txt', 'w') as f:
        f.write(parsedResult["GamePlayer2"])

    with open(dir + '/GameScore1.txt', 'w') as f:
        f.write(parsedResult["GameScore1"])

    with open(dir + '/GameScore2.txt', 'w') as f:
        f.write(parsedResult["GameScore2"])

    char1Request = requests.get(ip + '/' + parsedResult["GamePlayerCharacter1"] + '.png')
    with open(dir + '/GamePlayerCharacter1.png', 'wb') as f:
        f.write(char1Request.raw)

    char1Request = requests.get(ip + '/' + parsedResult["GamePlayerCharacter2"] + '.png')
    with open(dir + '/GamePlayerCharacter2.png', 'wb') as f:
        f.write(char1Request.raw)

    time.sleep(5)
