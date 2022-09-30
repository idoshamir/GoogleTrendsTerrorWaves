
from os import listdir
from os.path import isfile, join
import ast

dir = './tryouts/'

terrorNames = [
    "מהומות בנגב על רקע נטיעות קקל",
    "מבצע שומר החומות",
    "טרור עממי",
    "גל טרור הבודדים",
    "אירועי רמצאן 22"
]
terrorNamesSet = set(terrorNames)

files = [f for f in listdir(dir) if isfile(join(dir, f))]

peakCutOffs = {}
maxNumberOfPeaksBeforeTails = {}
daysOfTails = {}
minTailAverages = {}
maxNonTailAverages = {}
minNumberOfWordss = {}

def AddOne(dict, key):
    count = 0
    if key in dict:
        count = dict[key]
    count += 1
    dict[key] = count

for file in files:
    f = open(join(dir, file), "r")
    content = f.read()
    if content != '[]':
        matchedWaves = ast.literal_eval(content)
        terrorWavesFound = list(filter(lambda x: x in terrorNamesSet, matchedWaves))
        terrorWavesFoundCount = len(terrorWavesFound)
        nonTerrorWavesCount = len(matchedWaves) - terrorWavesFoundCount
        if terrorWavesFoundCount >= 2 and nonTerrorWavesCount == 1:
            split = file.split(';')
            peakCutOff = split[0]
            maxNumberOfPeaksBeforeTail = split[1]
            daysOfTail = split[2]
            minTailAverage = split[3]
            maxNonTailAverage = split[4]
            minNumberOfWords = split[5].split('.')[0]
            AddOne(peakCutOffs, peakCutOff)
            AddOne(maxNumberOfPeaksBeforeTails,maxNumberOfPeaksBeforeTail)
            AddOne(daysOfTails,daysOfTail)
            AddOne(minTailAverages,minTailAverage)
            AddOne(maxNonTailAverages,maxNonTailAverage)
            AddOne(minNumberOfWordss,minNumberOfWords)

print('peakCutOffs', dict(sorted(peakCutOffs.items(), key=lambda item: item[1])))
print('maxNumberOfPeaksBeforeTails', dict(sorted(maxNumberOfPeaksBeforeTails.items(), key=lambda item: item[1])))
print('daysOfTails', dict(sorted(daysOfTails.items(), key=lambda item: item[1])))
print('minTailAverages', dict(sorted(minTailAverages.items(), key=lambda item: item[1])))
print('maxNonTailAverages', dict(sorted(maxNonTailAverages.items(), key=lambda item: item[1])))
print('minNumberOfWordss', dict(sorted(minNumberOfWordss.items(), key=lambda item: item[1])))