#!/usr/bin/env python
import sys
import os
import ConfigParser
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from subprocess import call

names = ['dt', 'obs', 'err']
kgs2tpd = 86.4  # conversion kg/s to t/d

# configuration file
if (len(sys.argv) != 2):
    sys.exit('syntax mdoasplot.py config_file')
else:
    cfg = sys.argv[1]

# parse configuration file
config = ConfigParser.ConfigParser()
config.read(cfg)
webserver = config.get('web', 'server')
webuser = config.get('web', 'user')
webdir = config.get('web', 'dir')
xsize = float(config.get('plot', 'xsize'))
ysize = float(config.get('plot', 'ysize'))
ymax = float(config.get('plot', 'ymax'))
plotdir = config.get('plot', 'dir')
days = config.items('days')
sites = config.items('sites')

# loop through sites
for site in sites:
    siteid = site[1].split()[0].split('.')[0]
    networkid = site[1].split()[0].split('.')[1]
    typeid = site[1].split()[1]
    methodid = site[1].split()[2]
    print siteid, networkid, typeid, methodid

    # sitename meta data
    url = 'http://fits.geonet.org.nz/site'
    payload = {'siteID': siteid, 'networkID': networkid}
    r = requests.get(url, params=payload)
    # get from a dictionary
    jdata = r.json()
    jdict = jdata['features'][0]
    sitename = jdict['properties']['name'].encode('ascii', 'ignore')

    # unit meta data
    #url = 'http://fits.geonet.org.nz/type'
    #r = requests.get(url)
    # get from a dictionary
    #jdata = r.json()
    unit = 'kg/s'
    unit2 = 't/d'

    # loop through plot durations
    for id, day in days:
        url = 'https://fits.geonet.org.nz/observation?typeID=' + typeid + '&methodID=' + \
            methodid + '&siteID=' + siteid + \
            '&networkID=' + networkid + '&days=' + day
        df = pd.read_csv(
            url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

        fig, ax1 = plt.subplots(figsize=(xsize, ysize))

        # number obs per day
        dfcount = df['obs'].groupby(df['Datetime'].dt.date).count()
        dfcount.index = pd.to_datetime(dfcount.index)

        # min/max obs per day
        dfmin = df['obs'].groupby(df['Datetime'].dt.date).min()
        dfmax = df['obs'].groupby(df['Datetime'].dt.date).max()
        dfcount.index = pd.to_datetime(dfcount.index)
        ax1.bar(dfcount.index, dfmax - dfmin, bottom=dfmin, width=0.01,
                color='black', edgecolor='black', alpha=0.25, align='center', label='range')

        # mean per day
        dfmen = df['obs'].groupby(df['Datetime'].dt.date).mean()
        ax1.plot(dfcount.index, dfmen, marker='o', markersize=3,
                 color='red', linestyle='None', label='mean')
        # alternate y-axis
        ax2 = ax1.twinx()
        y1, y2 = ax1.get_ylim()
        ax2.set_ylim(0, ymax * kgs2tpd)
        dftpd = dfmen * kgs2tpd
        ax2.plot(dfcount.index, dftpd, marker='o', markersize=3,
                 color='red', linestyle='None', label='mean')

        # 25th and 75th percentile
        dfup = df['obs'].groupby(df['Datetime'].dt.date).quantile(0.75)
        dflp = df['obs'].groupby(df['Datetime'].dt.date).quantile(0.25)
        ax1.bar(dfcount.index, dfup - dflp, bottom=dflp, width=0.1,
                color='blue', edgecolor='blue', align='center', label='25th/75th %')

        ax1.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
        ax1.set_ylabel('SO2 flux (' + unit + ')')
        ax2.set_ylabel('SO2 flux (' + unit2 + ')', color='gray')
        ax2.tick_params(axis='y', colors='gray')
        ax1.legend(loc='upper left')
        ax1.set_ylim([0, ymax])
        plt.title(
            sitename + ', siteID =' + siteid + ', methodID = ' + methodid)

        # save plot
        if day == '365000':  # all data
            image = os.path.join(
                plotdir, siteid + '.' + networkid + '_' + typeid + '_' + methodid + '.png')
        else:
            image = os.path.join(
                plotdir, siteid + '.' + networkid + '_' + typeid + '_' + methodid + '_' + day + '.png')
        # print '  image file = ', image
        plt.savefig(image, dpi=200)
        cmdstr = '/usr/bin/scp ' + image + ' ' + \
            webuser + '@' + webserver + ':' + webdir
        call(cmdstr, shell=True)
