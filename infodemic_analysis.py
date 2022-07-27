#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  2 09:34:12 2021

@author: YOAV TEPPER

infodemic analysis: how COVID stats are related to google search trends

"""

# Import libraries
from multiprocessing.dummy import Pool as ThreadPool
from datetime import date, timedelta, datetime
#from pytrends.request import TrendReq
import pytrends
import matplotlib.pyplot as plt
from functools import reduce
import plotly.express as px
import seaborn as sns
import pandas as pd 
import numpy as np
import time

import urllib3, socket 
from urllib3.connection import HTTPConnection

#increase connection timeout which led to many failures    
HTTPConnection.default_socket_options = ( 
            HTTPConnection.default_socket_options + [
            (socket.SOL_SOCKET, socket.SO_SNDBUF, 1000000), #1MB in byte
            (socket.SOL_SOCKET, socket.SO_RCVBUF, 1000000)
        ])




outdir = "/Users/allyeran/Dropbox (HMS)/BGU/COVID_infodemic/"
#search_terms = ["COVID vaccine kills", "COVID vaccine scam", "loss of smell", "COVID booster shot", "COVID vaccine fertility", "COVID vaccine infertility", "dog", "plandemic"]
#search_terms = ["The Truth About COVID-19", "COVID vaccine scam", "loss of smell", "covid vaccine can kill", "COVID vaccine fertility", "COVID vaccine infertility", "vaccine kills", "plandemic", "coronavirus scam", "coronavirus hoax"]
search_terms = ["vaccine and period"]






#1. Plot the volume of searches between selected dates on a US map
pytrend = pytrends.request.TrendReq()
start_date = "2020-01-01"
end_date = "2021-12-01"

for search_term in search_terms:
# Fetch data from Google trends
    pytrend.build_payload(kw_list=[search_term], geo='US', timeframe=f'{start_date} {end_date}')
    google_trends = pytrend.interest_by_region(resolution='Country', inc_low_vol=True, inc_geo_code=True).reset_index()
    google_trends['code'] = google_trends['geoCode'].apply(lambda x: x.split('-')[1])

# Plot on map
    map_color = 'YlOrRd'
    fig = px.choropleth(google_trends,
                    locations="code",
                    color=search_term,
                    hover_name="geoName",
                    color_continuous_scale=map_color,
                    locationmode = 'USA-states')

    fig.update_coloraxes(cmid=50)
    fig.update_layout(title_text = f'\"{search_term}\" search volume by state, {start_date} to {end_date}', geo_scope='usa')
    fig.write_image(outdir+search_term + "_"+str(start_date)+"_"+str(end_date)+"_total_searches_per_state.png", engine="kaleido", scale=2)
    fig.show()
    
    

#2. Plot COVID stats between selected dates on a US map
# Get latest data CSV file (one day back is most up to date)
    start_date_for_COVID_stats = "04-12-2020"
    end_date_for_COVID_stats = "12-01-2021"


    # Create heatmap of normalized death ratio per state
    end_date_data = pd.read_csv(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/{end_date_for_COVID_stats}.csv')
    start_date_data = pd.read_csv(f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports_us/{start_date_for_COVID_stats}.csv')
    del_deaths = end_date_data.Deaths - start_date_data.Deaths
    end_date_data["Deaths"]= del_deaths
    end_date_data = end_date_data.join(google_trends.set_index('geoName'), on='Province_State', how='left')


    population = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')


    end_date_data = end_date_data.join(population.groupby(['Province_State']).sum()[['Population']], on='Province_State')
    end_date_data['DeathRatio'] = (end_date_data['Deaths'] / end_date_data['Population'])

    fig = px.choropleth(end_date_data,
                    locations="code",
                    color="DeathRatio",
                    hover_name="Province_State",
                    color_continuous_scale=map_color,
                    locationmode = 'USA-states')

    fig.update_coloraxes(cmin=0)
    fig.update_layout(title_text = 'COVID normalized deaths by state: '+start_date_for_COVID_stats+" to "+end_date_for_COVID_stats, geo_scope='usa')
    fig.write_image(outdir+start_date_for_COVID_stats+"_to_"+end_date_for_COVID_stats + "_normalized_deaths_by_state.png", engine="kaleido", scale=2)
    fig.show()
    
    
#3. Get google trends data by state
    # Build country name to country code mapping (using a dummy query which is a bit hacky, but does the job)
    pytrend = pytrends.request.TrendReq()
    pytrend.build_payload(kw_list=['covid'], geo='US', timeframe='2022-1-1 2022-1-2')
    country_map = pytrend.interest_by_region(resolution='Country', inc_low_vol=True, inc_geo_code=True)
    country_map = country_map.reset_index()[['geoName', 'geoCode']]

    #ready for action
    # Get Google trends data per state using a thread pool to speed up the process
    def get_trend(state):
        try:
            pytrend = pytrends.request.TrendReq()
            pytrend.build_payload(kw_list=[search_term], geo=state, timeframe=f'{start_date} {end_date}')
            result = pytrend.interest_over_time()
            result['geoCode'] = state
            result['keyword'] = search_term
            time.sleep(6)
        except pytrends.requests.exceptions.Timeout:
            print("Timeout!!!")
        print(f'Finished looking for \'{search_term}\' trend in \'{state}\'', end='\x1b[1K\r')
        return result.reset_index().rename(columns={search_term: 'value'})

    pool = ThreadPool() #2 Increasing this number will increase speed but might get you blocked by Google servers
    dfs = pool.map(get_trend, country_map['geoCode'].unique())

    # Merge results and join with country mapping        
    google_trends = pd.concat(dfs).sort_values(['date'])
    google_trends = google_trends.join(country_map.set_index('geoCode'), on='geoCode', how='left')


#4. Get vaccination data by state between the selected dates
# Disable chained assignment warning in Pandas
    pd.options.mode.chained_assignment = None

# Get Covid deaths time series
    covid_raw_series = pd.read_csv('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv')

# Get Covid vaccination time series
    vaccination_raw_series = pd.read_csv('https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/us_state_vaccinations.csv')
    vaccination_series = vaccination_raw_series[['location', 'date', 'daily_vaccinations']]
    vaccination_series['Date'] = vaccination_series['date'].astype('datetime64')

# Melt date columns into a single date column
    covid_series = covid_raw_series.groupby(['Province_State']).sum().reset_index()
    covid_series = covid_series.melt(id_vars=['Province_State'], value_vars=list(covid_series.columns[7:])).rename(columns={'variable': 'Date', 'value': 'Deaths'},)   
    covid_series['Date'] = covid_series['Date'].astype('datetime64')

# Enrich & normalize data
    covid_series = covid_series.join(covid_raw_series.groupby(['Province_State']).sum()[['Population']], on='Province_State')
    covid_series['DeathRatio'] = (covid_series['Deaths'] / covid_series['Population']) * 100

# Filter relevant dates
    vaccination_series = vaccination_series[(vaccination_series['Date'] >= np.datetime64(start_date)) & (vaccination_series['Date'] <= np.datetime64(end_date))]
    covid_series = covid_series[(covid_series['Date'] >= np.datetime64(start_date)) & (covid_series['Date'] <= np.datetime64(end_date))]

# Bucket dates by weeks (since google trends data is bucketed that way and we want a date-to-date match)
    covid_series = covid_series.sort_values(['Province_State', 'Date'])
    covid_series['Date'] = pd.to_datetime(covid_series['Date']) - pd.to_timedelta(7, unit='d')
    covid_series = covid_series.groupby(['Province_State', pd.Grouper(key='Date', freq='W-SUN')])['Deaths'].sum().reset_index().sort_values('Date')

    vaccination_series = vaccination_series.sort_values(['location', 'date'])
    vaccination_series['date'] = pd.to_datetime(vaccination_series['date']) - pd.to_timedelta(7, unit='d')
    vaccination_series = vaccination_series.groupby(['location', pd.Grouper(key='date', freq='W-SUN')])['daily_vaccinations'].sum().reset_index().sort_values('date')
    vaccination_series = vaccination_series.rename(columns={'location': 'Province_State', 'date': 'Date', 'daily_vaccinations': 'VaccinationsOnDate'})

# Manually fix state naming conventions so they will match between dataframes
    vaccination_series['Province_State'] = vaccination_series['Province_State'].replace("New York State", "New York")



#5. Split the data by state
    state_dfs = []

    for state in covid_series['Province_State'].unique():
        state_df = covid_series[covid_series['Province_State'] == state]    
        vaccine_df = vaccination_series[vaccination_series['Province_State'] == state]
    
    # Calculate diff from the cummulative raw data
        state_df['DeathsOnDate'] = state_df['Deaths'].diff()
    
    # Normalize values on scale of 0-100 to match Google trends data
        state_df['NDeaths'] = 100 * state_df['DeathsOnDate'] / state_df['DeathsOnDate'].max()    
        vaccine_df['NVaccinated'] = 100 * vaccine_df['VaccinationsOnDate'] / vaccine_df['VaccinationsOnDate'].max()
    
    # Join death & vaccination data with google trends data
        state_df = state_df[state_df['DeathsOnDate'] >= 0]  
        state_df = state_df.join(google_trends[google_trends['geoName'] == state].set_index('date'), on='Date', how='left')   
        state_df = state_df.merge(vaccine_df.set_index('Date'), on='Date', how='left')
        state_df = state_df.rename(columns={'Province_State_x': 'Province_State', 'keyword': 'Keyword', 'value': 'Value'})
    
    # Smoothen google trends data with a rolling mean
        state_df['RollingMean'] = state_df['Value'].rolling(window=3).mean()
        state_df['RollingMean'] = 100 * state_df['RollingMean'] / state_df['RollingMean'].max()
    
        state_dfs.append(state_df[['Province_State', 'Date', 'Keyword', 'RollingMean', 'Value', 'NDeaths', 'NVaccinated']])
        state_df.to_excel(outdir+search_term+"_"+state_df['Province_State'][0]+"_"+start_date+"_"+end_date+"_stats.xlsx")
        
    #Plot timeseries
        sns.set(rc={'figure.figsize':(15,5)})
        sns.set_style("whitegrid")
        line_width = 2
        #sns.lineplot(x="Date", y="NDeaths", data=state_df, color="#a83232", linewidth = line_width, label='NDeaths').grid(False)
        #sns.lineplot(x="Date", y="NVaccinated", data=state_df, color="#32a852", linewidth = line_width, label='NVaccinated').grid(False)
        #sns.lineplot(x="Date", y="RollingMean", data=state_df,  color="#3277a8", linewidth = 1, label=f'Normalized "{search_term}" searches').grid(False)
        #sns.lineplot(x="Date", y="Value", data=state_df,  color="grey", linewidth = 0.3, label=f'Raw "{search_term}" searches').grid(False)
        #sns.lineplot(x="Date", y="Value", data=state_df,  color="#3277a8", linewidth = line_width, label=f'Raw "{search_term}" searches').grid(False)
        
        
        sns.lineplot(x="Date", y="NDeaths", data=state_df, color="#a83232", linewidth = line_width).grid(False)
        sns.lineplot(x="Date", y="NVaccinated", data=state_df, color="#32a852", linewidth = line_width).grid(False)
        sns.lineplot(x="Date", y="Value", data=state_df,  color="#3277a8", linewidth = line_width).grid(False)
        
        sns.despine()
        plt.xticks(rotation=45)
        plt.title(f'Search trend and COVID19 stats in {state}')
        plt.savefig(outdir+search_term + "_"+state+"_"+str(start_date)+"_"+str(end_date)+"_timeseries.png")
        plt.show()
   
    print(f'Successfully created {len(state_dfs)} dataframes and generated their timeseries plots')



#7. Plot spearman correlations on US heatmap
    spearman_deaths = {}
    spearman_vaccinations = {}

    for state_df in state_dfs:
        state = state_df["Province_State"].iloc[0]
        print("Calculating correlations in "+str(state))
    
        # Calculate Spearman correlation
        expanded_df = state_df.groupby(['Province_State', 'Date', 'NDeaths', 'NVaccinated', 'Keyword'])['RollingMean'].aggregate('first').unstack().reset_index()
    
        try:
            corr = expanded_df[['NDeaths', 'NVaccinated'] + [search_term]].corr(method='spearman')
            matrix = np.triu(corr)
            spearman_deaths[state] = corr['NDeaths'][search_term] 
            spearman_vaccinations[state] = corr['NVaccinated'][search_term]
            country_map['spearman_death'] = country_map['geoName'].apply(lambda x: spearman_deaths[x] if x in spearman_deaths else None)       
            country_map['spearman_vaccinated'] = country_map['geoName'].apply(lambda x: spearman_vaccinations[x] if x in spearman_vaccinations else None) 
            country_map['code'] = country_map['geoCode'].apply(lambda x: x.split('-')[1])
        except Exception as e:
            print(f'Could not process data for state: {state}, error: {e}')
            country_map['spearman_death'] = country_map['geoName'].apply(lambda x: spearman_deaths[x] if x in spearman_deaths else None)       
            country_map['spearman_vaccinated'] = country_map['geoName'].apply(lambda x: spearman_vaccinations[x] if x in spearman_vaccinations else None) 
            country_map['code'] = country_map['geoCode'].apply(lambda x: x.split('-')[1])
    
        
    
# Plot Spearman correlation of search terms with with death trend
    fig = px.choropleth(country_map,
                    locations="code",
                    color="spearman_death",
                    hover_name="geoName",
                    color_continuous_scale='rdbu_r',
                    locationmode = 'USA-states')

    fig.update_coloraxes(cmid=0)
    fig.update_layout(title_text = f'Spearman correlations between "{search_term}" searches and death rate, {start_date} to {end_date}', geo_scope='usa')
    fig.write_image(outdir+search_term + "_"+str(start_date)+"_"+str(end_date)+"_spearman_bw_search_deaths_per_state.png", engine="kaleido", scale=2)
    fig.show()

# Plot spearman correlation of search terms with with vaccination trend
    fig = px.choropleth(country_map,
                    locations="code",
                    color="spearman_vaccinated",
                    hover_name="geoName",
                    color_continuous_scale='rdbu_r',
                    locationmode = 'USA-states')

    fig.update_coloraxes(cmid=0)
    fig.update_layout(title_text = f'Spearman correlations between "{search_term}" searches and vaccination rate, {start_date} to {end_date}', geo_scope='usa')
    fig.write_image(outdir+search_term + "_"+str(start_date)+"_"+str(end_date)+"_spearman_bw_search_vaccinations_per_state.png", engine="kaleido", scale=2)
    fig.show()
