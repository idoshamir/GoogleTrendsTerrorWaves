import pandas as pd
import json
import os
from pytrends.request import TrendReq

# code to export search periods JSON.stringify(arr.map(x => ({name: x.name, from: `${x.year_start}-${x.month_start.toString().padStart(2,'0')}-${x.day_start.toString().padStart(2,'0')} ${x.hour_start.toString().padStart(2,'0')}:00:00`, to: `${x.year_end}-${x.month_end.toString().padStart(2,'0')}-${x.day_end.toString().padStart(2,'0')} ${x.hour_end.toString().padStart(2,'0')}:59:59`})))

searchTermsFile = 'searchTerms.json'
searchPeriodsFile = 'searchPeriods.json'
resutlsFile = 'results.xlsx'

trendsSleep = 60

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
                curDf = pytrend.get_historical_interest([searchTerm], year_start=p["year_start"], month_start=p["month_start"], day_start=p["day_start"],
                                                    year_end=p["year_end"], month_end=p["month_end"], day_end=p["day_end"], cat=0, geo=geo, gprop='', sleep=trendsSleep, frequency='daily')
                curDf['periodName'] = p["name"]
                curDf['geo'] = geo
                curDf['searchTerm'] = searchTerm
                curDf.rename(columns = { searchTerm: 'value'}, inplace=True)
                curDf.to_pickle(curFilename)
                dfs.append(curDf)
            else:
                curDf = pd.read_pickle(curFilename)
                dfs.append(curDf)

df = pd.concat(dfs)

df.to_excel(resutlsFile)

print('done')
