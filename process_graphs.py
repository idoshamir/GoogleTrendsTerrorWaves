import pandas as pd
from os import listdir
from os.path import isfile, join
from os import rename
from scipy.signal import find_peaks,peak_prominences


mypath = '.'

def isPeakAtEnd(df):
    col = df.iloc[:, 0]
    peaks = list(find_peaks(col)[0])
    lastIndex = len(col)-1
    lastParts = set([lastIndex, lastIndex-1, lastIndex-2, lastIndex-3, lastIndex-4])
    found = [a for a in peaks if a in lastParts]
    return len(found) > 0

def getPeakScore(df):
    col = df.iloc[:, 0]
    lastIndex = len(col)-1
    lastParts = [lastIndex, lastIndex-1, lastIndex-2, lastIndex-3, lastIndex-4]
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
    lastParts = [lastIndex, lastIndex-1, lastIndex-2, lastIndex-3, lastIndex-4]
    maxLastParts = -1
    for i in lastParts:
        if col[i] > maxLastParts:
            maxLastParts = col[i]
    return maxLastParts

#pklFiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl')]
#for curFile in pklFiles:
#    curDf = pd.read_pickle(curFile)
#    score = getScore(curDf)
#    if isPeakAtEnd(curDf) and score >= 80:
#        rename(curFile, curFile + '2')

pkl2Files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl2')]
for curFile in pkl2Files:
    curDf = pd.read_pickle(curFile)
    score = getPeakScore(curDf)
    if score >= 80:
        rename(curFile, curFile + '2')
