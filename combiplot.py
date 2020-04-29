#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import sys
import os
import configparser
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import requests
from subprocess import call

def nameofsite(siteid):
    url = 'http://fits.geonet.org.nz/site'
    payload = {'siteID': siteid}
    r = requests.get(url,params=payload)
    #get from a dictionary
    jdata = r.json()
    jdict = jdata['features'][0]
    sitename = jdict['properties']['name']
    return sitename

def getsite(site):
    siteID = site.split()[0]
    typeID = site.split()[1]
    methodID = site.split()[2]
    return siteID, typeID, methodID

names = ['dt', 'obs', 'err']
kgs2tpd = 86.4  # conversion kg/s to t/d

# configuration file
if (len(sys.argv) != 2):
    sys.exit('syntax combiplot.py config_file')
else:
    cfg = sys.argv[1]

# parse configuration file
config = configparser.ConfigParser()
config.read(cfg)
webserver = config.get('web', 'server')
webuser = config.get('web', 'user')
webdir = config.get('web', 'dir')
xsize = float(config.get('plot', 'xsize'))
ysize = float(config.get('plot', 'ysize'))
ymax = float(config.get('plot', 'ymax'))
plotdir = config.get('plot', 'dir')
days = config.items('days')

# sites
site1 = config.get('sites', 'site1')
(siteID1, typeID1, methodID1) = getsite(site1)
site2 = config.get('sites', 'site2')
(siteID2, typeID2, methodID2) = getsite(site2)
site3 = config.get('sites', 'site3')
(siteID3, typeID3, methodID3) = getsite(site3)
site4 = config.get('sites', 'site4')
(siteID4, typeID4, methodID4) = getsite(site4)

unit = 'kg/s'
unit2 = 't/d'

# loop through plot durations
for id, day in days:
    # site1
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID1 + '&methodID=' + \
        methodID1 + '&siteID=' + siteID1 + \
        '&days=' + day
    df1 = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    # site2
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID2 + '&methodID=' + \
        methodID2 + '&siteID=' + siteID2 + \
        '&days=' + day
    df2 = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    # site3
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID3 + '&methodID=' + \
        methodID3 + '&siteID=' + siteID3 + \
        '&days=' + day
    df3 = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    # site4
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID4 + '&methodID=' + \
        methodID4 + '&siteID=' + siteID4 + \
        '&days=' + day
    df4 = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    # concatenate dataframes
    frames = [df1, df2, df3, df4]
    df = pd.concat(frames)

    df['tpd'] = df['obs'] * kgs2tpd

    #calculate daily counts of observations
    if (len(df1)>0):
        df1count = df1['obs'].groupby(df1['Datetime'].dt.date).count()
        df1count.index = pd.to_datetime(df1count.index)
    else:
        df1count = pd.DataFrame()

    if (len(df2)>0):
        df2count = df2['obs'].groupby(df2['Datetime'].dt.date).count()
        df2count.index = pd.to_datetime(df2count.index)
    else:
        df2count = pd.DataFrame()

    if (len(df3)>0):
        df3count = df3['obs'].groupby(df3['Datetime'].dt.date).count()
        df3count.index = pd.to_datetime(df3count.index)
    else:
        df3count = pd.DataFrame()

    if (len(df4)>0):
        df4count = df4['obs'].groupby(df4['Datetime'].dt.date).count()
        df4count.index = pd.to_datetime(df4count.index)
    else:
        df4count = pd.DataFrame()

    fig = plt.figure(figsize=(xsize, ysize))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1])
    ax1 = plt.subplot(gs[0])

    # sort by datetime and reindex
    df.sort_values('Datetime', inplace=True)
    df.reset_index(inplace=True)

    # number obs per day
    dfcount = df['obs'].groupby(df['Datetime'].dt.date).count()
    dfcount.index = pd.to_datetime(dfcount.index)

    # median per day
    dfmedian = df['tpd'].groupby(df['Datetime'].dt.date).median()
    ax1.plot(dfcount.index, dfmedian, marker='o', markersize=1.5,
             color='red', alpha=0.25, linestyle='None', label='median')

    # min/max obs per day
    #dfmin = df['tpd'].groupby(df['Datetime'].dt.date).min()
    dfmax = df['tpd'].groupby(df['Datetime'].dt.date).max()
    dfcount.index = pd.to_datetime(dfcount.index)
    ax1.bar(dfcount.index, dfmax - dfmedian, bottom=dfmedian, width=0.01,
            color='black', edgecolor='black', alpha=0.25, align='center', label='range')

    # max per day
    ax1.plot(dfcount.index, dfmax, marker='o', markersize=1.5,
             color='black', alpha=0.5, linestyle='None', label='max')

    # 25th and 75th percentile
    dfup = df['tpd'].groupby(df['Datetime'].dt.date).quantile(0.75)
    dflp = df['tpd'].groupby(df['Datetime'].dt.date).quantile(0.25)
    ax1.bar(dfcount.index, dfup - dflp, bottom=dflp, width=0.1,
            color='blue', edgecolor='blue', alpha=0.25, align='center', label='25th/75th %')

    ax1.grid(b=True, which='major', color='lightsalmon', linestyle='--', alpha=0.25)
    ax1.set_ylabel('SO2 flux (' + unit2 + ')')
    ax1.legend(loc='best', fontsize=8)
    ax1.set_ylim([0, ymax])
    plt.title('All observations')

    #number of observations
    ax2 = plt.subplot(gs[1])
    #site1
    sitename = nameofsite(siteID1)
    label = sitename+', assumed height'
    if len(df1count)>0:
        if methodID1 == 'mdoas-ch':
            ax2.plot(df1count, marker='o', markersize=3, color='red', linestyle='None', label=label)
        else:
            ax2.plot(df1count, marker='o', markersize=3, color='red', alpha=0.3, linestyle='None', label=label)
    #site2
    sitename = nameofsite(siteID2)
    label = sitename+', calculated height'
    if len(df2count)>0:
        if methodID2 == 'mdoas-ch':
            ax2.plot(df2count, marker='o', markersize=3, color='red', linestyle='None', label=label)
        else:
            ax2.plot(df2count, marker='o', markersize=3, color='red', alpha=0.3, linestyle='None', label=label)
    #site3
    sitename = nameofsite(siteID3)
    label = sitename+', assumed height'
    if len(df3count)>0:
        if methodID3 == 'mdoas-ch':
            ax2.plot(df3count, marker='o', markersize=3, color='blue', linestyle='None', label=label)
        else:
            ax2.plot(df3count, marker='o', markersize=3, color='blue', alpha=0.3, linestyle='None', label=label)
    #site4
    sitename = nameofsite(siteID4)
    label = sitename+', calculated height'
    if len(df4count)>0:
        if methodID4 == 'mdoas-ch':
            ax2.plot(df4count, marker='o', markersize=3, color='blue', linestyle='None', label=label)
        else:
            ax2.plot(df4count, marker='o', markersize=3, color='blue', alpha=0.3, linestyle='None', label=label)

    ax2.legend(loc='best', fontsize=8)
    ax2.set_ylabel('Numbers Obs')
    ax2.grid(b=True, which='major', color='lightsalmon', linestyle='--', alpha=0.25)

    # save plot
    if day == '365000':  # all data
        image = os.path.join(plotdir, 'mdoas.allobs.png')
    else:
        image = os.path.join(plotdir, 'mdoas.allobs_' + day + '.png')
    # print '  image file = ', image
    plt.savefig(image, dpi=200)
