import pandas as pd
from os import listdir
from os.path import isfile, join

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
    result[waveName][day].append(searchTerm)

waves = list(result.keys())
wavesUsed = set()
for wave in waves:
    days = list(result[wave].keys())
    maxWords = -1
    for day in days:
        length = len(result[wave][day])
        if length > maxWords:
            maxWords = length
    for day in days:
        length = len(result[wave][day])
        if length == maxWords:
            if wave not in wavesUsed:
                wirds = result[wave][day]
                for word in wirds:
                    fileNoExt = wave + ' IL ' + day + ' ' + word
                    file = fileNoExt + '.pkl22'
                    df = pd.read_pickle(file)
                    df.to_excel(fileNoExt + '.xlsx')
                    print(file)
                wavesUsed.add(wave)