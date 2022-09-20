from audioop import avg
from tkinter.tix import INTEGER
import pandas as pd
from os import listdir
from os.path import isfile, join
#from os import rename,remove
from scipy.signal import find_peaks,peak_prominences
from bidi import algorithm as bidialg
import json
from os.path import exists
import ast
import time

mypath = '.'

#peakCutOff = 90
#maxNumberOfPeaksBeforeTail = 5
#daysOfTail = 5
#minTailAverage = 70
#maxNonTailAverage = 30
#minNumberOfWords = 3

peakCutOffs = range(80,100)
maxNumberOfPeaksBeforeTails = range(0,3)
daysOfTails = range(1,5)
minTailAverages = range(80,100)
maxNonTailAverages = range(0,30)
minNumberOfWordsArr = range(2,5)

terrorNames = [
    "מהומות בנגב על רקע נטיעות קקל",
    "מבצע שומר החומות",
    "טרור עממי",
    "גל טרור הבודדים",
    "אירועי רמצאן 22"
]
terrorNamesSet = set(terrorNames)

searchTermsFile = 'searchTerms.json'
searchTermsHebrewFile = 'searchTermsHebrew.json'

def loadJsonFile(file):
    with open(file, encoding='utf-8') as f:
        return json.load(f)

searchTerms = loadJsonFile(searchTermsFile)
searchTermsHebrew = loadJsonFile(searchTermsHebrewFile)

def countBeforePeak(df, score, daysOfTail):
    col = list(df.iloc[:, 0])[:-daysOfTail]
    filtered = list(filter(lambda x: x >= score, col)) 
    return len(filtered)

def isPeakAtEnd(df, daysOfTail):
    col = df.iloc[:, 0]
    peaks = list(find_peaks(col)[0])
    lastIndex = len(col)-1
    lastParts = []
    i = daysOfTail
    while i > 0:
        lastParts = [lastIndex-i]
        i -= 1
    found = [a for a in peaks if a in set(lastParts)]
    return len(found) > 0

def getAverageTail(df, daysOfTail):
    col = df.iloc[:, 0]
    lastIndex = len(col)-1
    lastParts = []
    i = daysOfTail
    while i > 0:
        lastParts = [lastIndex-i]
        i -= 1
    sum = 0
    for i in lastParts:
        sum += col[i]
    return sum/len(lastParts)

def getAverageNonTail(df, daysOfTail):
    col = df.iloc[:, 0]
    lastIndex = len(col)-1
    lastParts = []
    i = daysOfTail
    while i > 0:
        lastParts = [lastIndex-i]
        i -= 1
    sum = 0
    for i in range(len(col)):
        if i not in lastParts:
            sum += col[i]
    return sum/(len(col)-len(lastParts))

def getPeakScore(df, daysOfTail):
    col = df.iloc[:, 0]
    lastIndex = len(col)-1
    lastParts = []
    i = daysOfTail
    while i > 0:
        lastParts = [lastIndex-i]
        i -= 1
    peaks, _ = find_peaks(col)
    prominences = list(peak_prominences(col, peaks)[0])
    peaksList = list(peaks)
    maxLastParts = -1
    for lastPart in lastParts:
        i = 0
        for curPeak in peaksList:
            if curPeak == lastPart:
                prominence = prominences[i]
                if prominence > maxLastParts:
                    maxLastParts = prominence
            i += 1
    return maxLastParts

def getMaxAtTail(df, daysOfTail):
    col = df.iloc[:, 0]
    lastIndex = len(col)-1
    lastParts = []
    i = daysOfTail
    while i > 0:
        lastParts = [lastIndex-i]
        i -= 1
    maxLastParts = -1
    for i in lastParts:
        if col[i] > maxLastParts:
            maxLastParts = col[i]
    return maxLastParts

# back to pkl files
#pklFiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and (f.endswith('.pkl2') or f.endswith('.pkl22'))]
#for curFile in pklFiles:
#    oldFile = curFile.replace('.pkl22','.pkl').replace('.pkl2','.pkl')
#    if exists(oldFile):
#        remove(curFile)
#    else:
#        rename(curFile, oldFile)

def getTerrorWaves(peakCutOff, maxNumberOfPeaksBeforeTail, daysOfTail, minTailAverage, maxNonTailAverage, minNumberOfWords):
    res = []
    pkl2Files = []
    pklFiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl')]
    for curFile in pklFiles:
        curDf = pd.read_pickle(curFile)
        maxAtTail = getMaxAtTail(curDf, daysOfTail)
        if isPeakAtEnd(curDf, daysOfTail) and maxAtTail >= peakCutOff and countBeforePeak(curDf, peakCutOff, daysOfTail) <= maxNumberOfPeaksBeforeTail:
            pkl2Files.append(curFile)
            #rename(curFile, curFile + '2')
    pkl22Files = []
    #pkl2Files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl2')]
    for curFile in pkl2Files:
        curDf = pd.read_pickle(curFile)
        maxAtTail = getPeakScore(curDf, daysOfTail)
        avgTail = getAverageTail(curDf, daysOfTail)
        avgNonTail = getAverageNonTail(curDf, daysOfTail)
        if maxAtTail >= peakCutOff and avgTail >= minTailAverage and avgNonTail <= maxNonTailAverage:
            pkl22Files.append(curFile)
            #rename(curFile, curFile + '2')

    #pkl2Files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl22')]
    result = {}

    for file in pkl22Files:
        split = file.split('.')[0].split(' IL ')
        waveName = split[0]
        split2 = split[1].split(' ')
        day = split2[0]
        searchTerm = split2[1]
        if waveName not in result:
            result[waveName] = {}
        if day not in result[waveName]:
            result[waveName][day] = []
        if searchTerm in searchTerms:
            result[waveName][day].append(searchTerm)

    waves = list(result.keys())
    wavesUsed = set()
    for wave in waves:
        days = list(result[wave].keys())
        maxWords = -1
        for day in days:
            length = len(result[wave][day])
            if length > maxWords and length > 1:
                maxWords = length
        if maxWords >= minNumberOfWords:
            for day in days:
                length = len(result[wave][day])
                if length == maxWords:
                    if wave not in wavesUsed:
                        # words = result[wave][day]
                        # allDf = None
                        # firstDf = True
                        # for word in words:
                        #     fileNoExt = wave + ' IL ' + day + ' ' + word
                        #     file = fileNoExt + '.pkl'
                        #     if firstDf:
                        #         allDf = pd.read_pickle(file)
                        #         allDf.drop(['isPartial', 'periodName', 'geo', 'searchTerm'], inplace=True, axis=1)
                        #         cols = allDf.columns.values.tolist()
                        #         for col in cols:
                        #             searchTermIndex = searchTerms.index(col)
                        #             searchTermHebrew = searchTermsHebrew[searchTermIndex]
                        #             allDf.rename(columns={col: bidialg.get_display(col + ' - ' + searchTermHebrew)}, inplace=True)
                        #         firstDf = False
                        #     else:
                        #         df = pd.read_pickle(file)
                        #         df.drop(['isPartial', 'periodName', 'geo', 'searchTerm'], inplace=True, axis=1)
                        #         cols = df.columns.values.tolist()
                        #         for col in cols:
                        #             searchTermIndex = searchTerms.index(col)
                        #             searchTermHebrew = searchTermsHebrew[searchTermIndex]
                        #             df.rename(columns={col: bidialg.get_display(col + ' - ' + searchTermHebrew)}, inplace=True)
                        #         allDf = allDf.join(df)
                            #df.to_excel(fileNoExt + '.xlsx')
                            #print(file)
                        #text = bidialg.get_display(wave)
                        #allDf.plot(title=text)
                        #plt.show()
                        wavesUsed.add(wave)
                        res.append(wave)
    return res

maxTerrorWavesFoundCount = -1
minNotTerrorWavesCount = 100000000
bestPeakCutOff = -1
bestMaxNumberOfPeaksBeforeTail = 100000000
bestDaysOfTail = -1
bestMinTailAverage = -1
bestMaxNonTailAverage = 100000000
bestMinNumberOfWords = -1

retryCount = 10

for peakCutOff in peakCutOffs:
    for maxNumberOfPeaksBeforeTail in maxNumberOfPeaksBeforeTails:
        for daysOfTail in daysOfTails:
            for minTailAverage in minTailAverages:
                for maxNonTailAverage in maxNonTailAverages:
                    for minNumberOfWords in minNumberOfWordsArr:
                        retryNum = 0
                        file = f'./tryouts/{peakCutOff};{maxNumberOfPeaksBeforeTail};{daysOfTail};{minTailAverage};{maxNonTailAverage};{minNumberOfWords}.txt'
                        matchedWaves = None
                        if exists(file):
                            file = open(file, "r")
                            content = file.read()
                            matchedWaves = ast.literal_eval(content)
                        else:
                            try:
                                matchedWaves = getTerrorWaves(peakCutOff, maxNumberOfPeaksBeforeTail, daysOfTail, minTailAverage, maxNonTailAverage, minNumberOfWords)
                                f = open(file, "w+")
                                f.write(str(matchedWaves))
                                f.close()
                            except:
                                print('retry')
                                retryNum += 1
                                if retryNum > retryCount:
                                   raise
                                time.sleep(60)
                        terrorWavesFound = list(filter(lambda x: x in terrorNamesSet, matchedWaves))
                        terrorWavesFoundCount = len(terrorWavesFound)
                        nonTerrorWavesCount = 13 - terrorWavesFoundCount
                        if terrorWavesFoundCount >= maxTerrorWavesFoundCount:
                            if nonTerrorWavesCount <= minNotTerrorWavesCount:
                                maxTerrorWavesFoundCount = terrorWavesFoundCount
                                minNotTerrorWavesCount = nonTerrorWavesCount
                                bestPeakCutOff = peakCutOff
                                bestMaxNumberOfPeaksBeforeTail = maxNumberOfPeaksBeforeTail
                                bestDaysOfTail = daysOfTail
                                bestMinTailAverage = minTailAverage
                                bestMaxNonTailAverage = maxNonTailAverage
                                bestMinNumberOfWords = minNumberOfWords
                                print("-")
                                print(f"maxTerrorWavesFoundCount: {maxTerrorWavesFoundCount} minNotTerrorWavesCount: {minNotTerrorWavesCount}")
                                print(f"bestPeakCutOff: {bestPeakCutOff}")
                                print(f"bestMaxNumberOfPeaksBeforeTail: {bestMaxNumberOfPeaksBeforeTail}")
                                print(f"bestDaysOfTail: {bestDaysOfTail}")
                                print(f"bestMinTailAverage: {bestMinTailAverage}")
                                print(f"bestMaxNonTailAverage: {bestMaxNonTailAverage}")
                                print(f"bestMinNumberOfWords: {bestMinNumberOfWords}")

print("-")
print(f"maxTerrorWavesFoundCount: {maxTerrorWavesFoundCount} minNotTerrorWavesCount: {minNotTerrorWavesCount}")
print(f"bestPeakCutOff: {bestPeakCutOff}")
print(f"bestMaxNumberOfPeaksBeforeTail: {bestMaxNumberOfPeaksBeforeTail}")
print(f"bestDaysOfTail: {bestDaysOfTail}")
print(f"bestMinTailAverage: {bestMinTailAverage}")
print(f"bestMaxNonTailAverage: {bestMaxNonTailAverage}")
print(f"bestMinNumberOfWords: {bestMinNumberOfWords}")