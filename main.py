import pandas as pd
import json
from pytrends.request import TrendReq

# code to export search periods JSON.stringify(arr.map(x => ({name: x.name, from: `${x.year_start}-${x.month_start.toString().padStart(2,'0')}-${x.day_start.toString().padStart(2,'0')} ${x.hour_start.toString().padStart(2,'0')}:00:00`, to: `${x.year_end}-${x.month_end.toString().padStart(2,'0')}-${x.day_end.toString().padStart(2,'0')} ${x.hour_end.toString().padStart(2,'0')}:59:59`})))

searchTermsFile = 'searchTerms.json'
searchPeriodsFile = 'searchPeriods.json'
resutlsFile = 'results.csv'

geos = ['IL', 'PS']


def loadJsonFile(file):
    with open(file, encoding='utf-8') as f:
        return json.load(f)


searchTerms = loadJsonFile(searchTermsFile)
periods = loadJsonFile(searchPeriodsFile)

pytrend = TrendReq()

df = pd.DataFrame()

for p in periods:
    for geo in geos:
        for searchTerm in searchTerms:
            print('"' + p["name"] + '" (' + geo + '): ' + searchTerm)
            df1 = pytrend.get_historical_interest(searchTerm, year_start=p["year_start"], month_start=p["month_start"], day_start=p["day_start"],
                                                hour_start=p["hour_start"], year_end=p["year_end"], month_end=p["month_end"], day_end=p["day_end"], hour_end=p["hour_end"], cat=0, geo=geo, gprop='', sleep=0)
            df1['name'] = p["name"]
            df1['geo'] = geo
            df1['searchTerm'] = searchTerm
            df.combine(df1)
            #print(df.to_string())

df.to_csv(resutlsFile, index=False)
print('done')
