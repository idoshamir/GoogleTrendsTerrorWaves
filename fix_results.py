import pandas as pd
import csv

file = "results5.xlsx"
resultFile = "results6.csv"

def calcScore(row, keys):
    sum = 0
    totalCount = 0
    for key in keys:
        score = int(row[key])
        weight = 1
        if key == "شهادة" or key == "عملية":
            weight = 1
        sum += score*weight
        totalCount += weight
    return round(sum/totalCount)

df = pd.read_excel(file).fillna(value=0)

resultDict = {}

for index, row in df.iterrows():
    keys = row.keys()
    resultKeys = list(filter(lambda key: key not in ['date','isPartial','periodName','geo','searchTerm'] , keys))
    dateFixed = str(row["date"]).split(' ')[0]
    isPS = row["geo"] == "PS"
    periodName = row["periodName"]
    key = f'{dateFixed};{periodName}'
    if not isPS:
        if key not in resultDict:
            row["day"] = dateFixed
            row["score"] = calcScore(row, resultKeys)
            resultDict[key] = row
        else:
            r = resultDict[key]
            score = round((r["score"] + calcScore(row, resultKeys))/2)
            r["score"] = score
            resultDict[key] = r
        #for k in keys:
                #if k != 'date' and k != 'geo' and k != 'periodName':
                #    (resultDict[key])[k] += row[k]
keys = list(resultDict.keys())
result = []
for key in keys:
    result.append(resultDict[key])

keys = ["day", "periodName", "score"] #result[0].keys()

with open(resultFile, 'w', encoding='utf-8-sig', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    for row in result:
        keys_values = row.items()
        newRow = {str(key): str(value) for key, value in keys_values}
        writeRow = {}
        writeRow["day"] = newRow["day"]
        writeRow["periodName"] = newRow["periodName"]
        writeRow["score"] = newRow["score"]
        dict_writer.writerow(writeRow)
