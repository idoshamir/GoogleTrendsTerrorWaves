import pandas as pd
import json
import os
import time
from datetime import datetime, timedelta
from pytrends.request import TrendReq

# code to export search periods JSON.stringify(arr.map(x => ({name: x.name, from: `${x.year_start}-${x.month_start.toString().padStart(2,'0')}-${x.day_start.toString().padStart(2,'0')} ${x.hour_start.toString().padStart(2,'0')}:00:00`, to: `${x.year_end}-${x.month_end.toString().padStart(2,'0')}-${x.day_end.toString().padStart(2,'0')} ${x.hour_end.toString().padStart(2,'0')}:59:59`})))

searchTermsFile = 'searchTerms.json'
searchPeriodsFile = 'searchPeriods.json'
resutlsFile = 'results7.xlsx'

trendsSleep = 10

lookBackMonths = 2

geos = ['IL'] #['IL', 'PS']

def loadJsonFile(file):
    with open(file, encoding='utf-8') as f:
        return json.load(f)

searchTerms = loadJsonFile(searchTermsFile)
periods = loadJsonFile(searchPeriodsFile)

pytrend = TrendReq()

dfs = []

for p in periods:
    name = p["name"]
    for geo in geos:
        for searchTerm in searchTerms:
            periodStartDate = datetime.strptime(p["period_start_date"], "%Y-%m-%d") + timedelta(days=3)
            periodEndDate = datetime.strptime(p["period_end_date"], "%Y-%m-%d")
            while periodStartDate < periodEndDate:
                startDate = periodStartDate - timedelta(days=30*lookBackMonths)
                endDate = periodStartDate.strftime("%Y-%m-%d")
                curFilename = name + ' ' + geo + ' ' + endDate + ' ' + searchTerm + '.pkl'
                if not os.path.exists(curFilename):
                    print('"' + name + '" (' + geo + ') ' + endDate + ': ' + searchTerm)
                    retryNum = 1
                    retryCount = 6
                    pytrend.build_payload(kw_list=[f'"{[searchTerm]}"'], geo=geo, timeframe=f'{startDate.strftime("%Y-%m-%d")} {endDate}')
                    while retryNum <= retryCount:
                        try:
                            curDf = pytrend.interest_over_time()
                            curDf['periodName'] = name
                            curDf['geo'] = geo
                            curDf['searchTerm'] = searchTerm
                            curDf.rename(columns = { f'"{[searchTerm]}"': searchTerm}, inplace=True)
                            #print(curDf.to_string())
                            curDf.to_pickle(curFilename)
                            dfs.append(curDf)
                            time.sleep(trendsSleep)
                            break
                        except:
                            retryNum += 1
                            if retryNum > retryCount:
                                raise
                            time.sleep(20)
                else:
                    curDf = pd.read_pickle(curFilename)
                    #curDf.rename(columns = { f'"{[searchTerm]}"': searchTerm}, inplace=True)
                    dfs.append(curDf)
                periodStartDate = periodStartDate + timedelta(days=1)

df = pd.concat(dfs)
df.sort_values(df.columns[0])

df.to_excel(resutlsFile)

print('done')
