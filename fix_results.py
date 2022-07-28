import pandas as pd
import csv

file = "results3.xlsx"
resultFile = "results4.csv"

df = pd.read_excel(file).fillna(value=0)

resultDict = {}

for index, row in df.iterrows():
    keys = row.keys()
    key = f'{str(row["date"])};{row["geo"]};{row["periodName"]}'
    if key not in resultDict:
        resultDict[key] = row
    else:
        for k in keys:
                if k != 'date' and k != 'geo' and k != 'periodName':
                    (resultDict[key])[k] += row[k]
keys = list(resultDict.keys())
result = []
for key in keys:
    result.append(resultDict[key])

keys = result[0].keys()

with open(resultFile, 'w', encoding='utf8', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    for row in result:
        keys_values = row.items()
        newRow = {str(key): str(value) for key, value in keys_values}
        dict_writer.writerow(newRow)
