import pandas as pd
from os import listdir
from os.path import isfile, join
from os import rename
from scipy.signal import find_peaks


mypath = '.'

def isPeakAtEnd(df):
    col = df.iloc[:, 0]
    peaks = list(find_peaks(col)[0])
    lastIndex = len(col)-1
    lastParts = set([lastIndex, lastIndex-1, lastIndex-2, lastIndex-3, lastIndex-4])
    found = [a for a in peaks if a in lastParts]
    return len(found) > 0

def getScore(df):
    col = df.iloc[:, 0]
    lastIndex = len(col)-1
    lastParts = [lastIndex, lastIndex-1, lastIndex-2, lastIndex-3, lastIndex-4]
    maxLastParts = -1
    for i in lastParts:
        if col[i] > maxLastParts:
            maxLastParts = col[i]
    return maxLastParts

pklFiles = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl')]
for curFile in pklFiles:
    curDf = pd.read_pickle(curFile)
    score = getScore(curDf)
    if isPeakAtEnd(curDf) and score >= 80:
        rename(curFile, curFile + '2')

pkl2Files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl2')]
for curFile in pkl2Files:
    curDf = pd.read_pickle(curFile)
print(len(pkl2Files))
