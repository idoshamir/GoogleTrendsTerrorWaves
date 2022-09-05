import pandas as pd
from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from bidi import algorithm as bidialg
import json

searchTermsFile = 'searchTerms.json'

def loadJsonFile(file):
    with open(file, encoding='utf-8') as f:
        return json.load(f)

searchTerms = loadJsonFile(searchTermsFile)

mypath = '.'

pkl2Files = [f for f in listdir(mypath) if isfile(join(mypath, f)) and f.endswith('.pkl22')]

result = {}

for file in pkl2Files:
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
    if maxWords > 1:
        for day in days:
            length = len(result[wave][day])
            if length == maxWords:
                if wave not in wavesUsed:
                    words = result[wave][day]
                    allDf = None
                    firstDf = True
                    for word in words:
                        fileNoExt = wave + ' IL ' + day + ' ' + word
                        file = fileNoExt + '.pkl22'
                        if firstDf:
                            allDf = pd.read_pickle(file)
                            allDf.drop(['isPartial', 'periodName', 'geo', 'searchTerm'], inplace=True, axis=1)
                            firstDf = False
                        else:
                            df = pd.read_pickle(file)
                            df.drop(['isPartial', 'periodName', 'geo', 'searchTerm'], inplace=True, axis=1)
                            allDf = allDf.join(df)
                        #df.to_excel(fileNoExt + '.xlsx')
                        #print(file)
                    text = bidialg.get_display(wave)
                    allDf.plot(title=text)
                    plt.show()
                    wavesUsed.add(wave)