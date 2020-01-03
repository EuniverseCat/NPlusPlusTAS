from urllib.request import urlopen
from urllib.error import HTTPError
import json
import time
import zlib

IGNORED_PLAYERS = [
  "Kronogenics",
  "BlueIsTrue",
  "fiordhraoi",
  "cheeseburgur101",
  "Jey",
  "jungletek",
  "Hedgy",
  "ᕈᘎᑕᒎᗩn ᙡiᗴᒪḰi",
  "Venom",
  "EpicGamer10075",
  "Altii",
  "Puςe",
  "Floof The Goof",
]

tabOffsets = {'SI':0, 'S':600, 'SU':2400, 'SL':1200, 'Q':1800 , '!':3000}
rowSizes = {'SI':5, 'S':20, 'SU':20, 'SL':20, 'Q':4, '!':4}
rowOffsets = {'A':0, 'B':1, 'C':2, 'D':3, 'E':4, 'X':5}

def scoresUri(level):
    uri = "https://dojo.nplusplus.ninja/prod/steam/get_scores?steam_id={0}&steam_auth=&level_id={1}"
    uri = uri.format(steamID, level)
    return uri

def replayUri(replay):
    uri = "https://dojo.nplusplus.ninja/prod/steam/get_replay?steam_id={0}&steam_auth=&replay_id={1}"
    uri = uri.format(steamID, replay)
    return uri

def parseLevelID(ID):
    try:                                                                    
        sections = ID.upper().split("-")
        tab = sections[0]
        row = sections[1]
        if tab == "Q" or tab == "!":
            episode = 0
            level = int(sections[2])
            if level > 23:
                return None
            levelID = tabOffsets[tab] + level * 5 + rowOffsets[row] / 5
            return levelID
        else:
            episode = int(sections[2])
            level = int(sections[3])
        if (row == 'X' and tab == 'SI') or episode >= rowSizes[tab]  or level > 4:
            return None
        if row == 'X':
            levelID = tabOffsets[tab] + rowSizes[tab] * 25 + episode * 5 + level
        else:
            levelID = levelID = tabOffsets[tab] + episode * 25 + rowOffsets[row] + level
        return levelID
    except:
        return None

def NametoID(name):
    pass

def GetScores(nameorID, rank, toRank = None):
    if not toRank: toRank = rank + 1
    else: toRank += 1
    try:
        ID = int(nameorID)
    except ValueError:
        ID = parseLevelID(nameorID)
        if ID == None:
            ID = NametoID(nameorID)
            if ID == None:
                print("Level not found.")
                return
    for i in range(6):
        if i == 5:
            return None
        try:
            scores = json.loads(urlopen(scoresUri(ID)).read())
            if scores == -1337:
                print("Connection expired. Press enter after reconnecting to Metanet servers.")
                input()
                continue
            break
        except HTTPError:
            print("HTTP Error. Press enter to try again.")
            input()
    
    scores = scores['scores']
    ignored = 0
    i = 0
    entries = []
    while i - ignored < toRank and i < 20:
        entry = scores[i]
        if entry['user_name'] in IGNORED_PLAYERS:
            ignored += 1
        elif i - ignored >= rank:
            entries.append((entry['score'], entry['replay_id'], entry['user_name']))
        i += 1
    return entries

def SaveReplay(nameorID, rank, toRank = None):
    scores = GetScores(nameorID, rank, toRank)
    if scores == None:
        return
    if scores == []:
        print("Replay not found.")
        return
    for score, replayID, name in scores:
        for i in range(5):
            try:
                replay = urlopen(replayUri(replayID)).read()
                if replay == '-1337':
                    print("Connection expired. Press enter after reconnecting to Metanet servers.")
                    input()
                    continue
                break
            except HTTPError:
                print("HTTP Error. Press enter to try again.")
        replay = zlib.decompress(replay[16:])[30:]
        filename = f'{nameorID} - {score} - {name}.ltm'
        output = open(filename, 'w')
        for frame in replay:
            inputs = ''
            if frame | 1 == frame: inputs += '007a:'
            if frame | 2 == frame: inputs += 'ff53:'
            if frame | 4 == frame: inputs += 'ff51:'
            inputs = '|' + inputs[:-1] + '|\n'
            output.write(inputs)
        output.close()
        print(f'Saved {filename}')

steamID = input("Enter Steam ID #: ")
while True:
    level = input("Enter in-game or Metanet level ID. (q to quit)\n")
    if level == "":
        continue
    if level.lower() == 'q':
        break
    if level[0] == '?':
        level = 'Q' + level[1:]
    try:
        rank = int(input("Enter rank of replay to convert.\n"))
    except ValueError:
        print("Invalid rank.")
        continue
    SaveReplay(level, rank)
