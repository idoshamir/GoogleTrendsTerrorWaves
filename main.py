import pandas as pd
import json
import os
import time
from pytrends.request import TrendReq

# code to export search periods JSON.stringify(arr.map(x => ({name: x.name, from: `${x.year_start}-${x.month_start.toString().padStart(2,'0')}-${x.day_start.toString().padStart(2,'0')} ${x.hour_start.toString().padStart(2,'0')}:00:00`, to: `${x.year_end}-${x.month_end.toString().padStart(2,'0')}-${x.day_end.toString().padStart(2,'0')} ${x.hour_end.toString().padStart(2,'0')}:59:59`})))

searchTermsFile = 'searchTerms.json'
searchPeriodsFile = 'searchPeriods.json'
resutlsFile = 'results3.xlsx'

trendsSleep = 10

geos = ['IL', 'PS']

def loadJsonFile(file):
    with open(file, encoding='utf-8') as f:
        return json.load(f)

searchTerms = loadJsonFile(searchTermsFile)
periods = loadJsonFile(searchPeriodsFile)

pytrend = TrendReq()

dfs = []

for p in periods:
    for geo in geos:
        for searchTerm in searchTerms:
            curFilename = p["name"] + ' ' + geo + ' ' + searchTerm + '.pkl'
            if not os.path.exists(curFilename):
                print('"' + p["name"] + '" (' + geo + '): ' + searchTerm)
                pytrend.build_payload(kw_list=[f'"{[searchTerm]}"'], geo=geo, timeframe=f'{p["start_date"]} {p["end_date"]}')
                curDf = pytrend.interest_over_time()
                curDf['periodName'] = p["name"]
                curDf['geo'] = geo
                curDf['searchTerm'] = searchTerm
                curDf.rename(columns = { f'"{[searchTerm]}"': 'value'}, inplace=True)
                #print(curDf.to_string())
                curDf.to_pickle(curFilename)
                dfs.append(curDf)
                time.sleep(trendsSleep)
            else:
                curDf = pd.read_pickle(curFilename)
                curDf.rename(columns = { f'"{[searchTerm]}"': searchTerm}, inplace=True)
                dfs.append(curDf)

df = pd.concat(dfs)
df.sort_values(df.columns[0])

df.to_excel(resutlsFile)

print('done')
