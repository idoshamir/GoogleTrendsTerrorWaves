import pandas as pd
from os import listdir
from os.path import isfile, join
from os import rename,remove
from scipy.signal import find_peaks,peak_prominences
from os.path import exists

mypath = '.'

peakCutOff = 90
maxNumberOfPeaksBeforeTail = 1
daysOfTail = 3

def countBeforePeak(df, score):
    col = list(df.iloc[:, 0])[:-5]
    filtered = list(filter(lambda x: x >= score, col)) 
    return len(filtered)

def isPeakAtEnd(df):
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

def getPeakScore(df):
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

def getScore(df):
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
pklFiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and (f.endswith('.pkl2') or f.endswith('.pkl22'))]
for curFile in pklFiles:
    oldFile = curFile.replace('.pkl22','.pkl').replace('.pkl2','.pkl')
    if exists(oldFile):
        remove(curFile)
    else:
        rename(curFile, oldFile)

pklFiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl')]
for curFile in pklFiles:
    curDf = pd.read_pickle(curFile)
    score = getScore(curDf)
    if isPeakAtEnd(curDf) and score >= peakCutOff and countBeforePeak(curDf, peakCutOff) <= maxNumberOfPeaksBeforeTail:
        rename(curFile, curFile + '2')

pkl2Files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl2')]
for curFile in pkl2Files:
    curDf = pd.read_pickle(curFile)
    score = getPeakScore(curDf)
    if score >= peakCutOff:
        rename(curFile, curFile + '2')
