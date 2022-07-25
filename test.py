import pandas as pd
from pytrends.request import TrendReq

pytrend = TrendReq()

dr = pytrend.get_historical_interest(['hello'], year_start=2022, month_start=1, day_start=1,
                                                year_end=2022, month_end=1, day_end=31, cat=0, geo='', gprop='', sleep=60, frequency='daily')
print(dr.to_string())
print('done')
