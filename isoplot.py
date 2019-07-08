#!/usr/bin/env python

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import requests
import numpy as np
from dateutil import parser
import sys
import os
import ConfigParser

names = ['dt', 'obs', 'err']

# configuration file
if (len(sys.argv) != 2):
    sys.exit('syntax isoplot.py config_file')
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
plotdir = config.get('plot', 'dir')
sites = config.items('sites')

for site in sites:
    # first data set
    siteID = site[1].split()[0]
    typeID = site[1].split()[1]

    # site meta data
    url = 'http://fits.geonet.org.nz/site'
    payload = {'siteID': siteID}
    r = requests.get(url, params=payload)
    jdata = r.json()
    sitename = jdata.values()[1][0]['properties']['name'].encode('ascii', 'ignore')

    # figure set up
    fig = plt.figure(figsize=(xsize, ysize))

    # time series data and plot
    ax = fig.add_subplot(1, 1, 1)
    url = 'https://fits.geonet.org.nz/observation?typeID=' +     typeID + '&siteID=' + siteID
    dfo = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    # meta data for last observation
    url = 'http://fits.geonet.org.nz/observation/stats'
    payload = {'typeID': typeID, 'siteID': siteID}
    r = requests.get(url, params=payload)
    jdata = r.json()
    last = jdata.get('Last').get('DateTime').encode('ascii', 'ignore')
    dtlast = parser.parse(last)
    strlast = dtlast.strftime("%Y-%m-%d")

    # 2nd data set
    typeID = site[1].split()[2]
    url = 'https://fits.geonet.org.nz/observation?typeID=' +     typeID + '&siteID=' + siteID
    dfh = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    # plot data for site
    plt.scatter(dfo['obs'], dfh['obs'], marker='o', color='black', label='all obs')
    # plot recent data
    plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='red', s=100, label='last obs')  # last

    #plot contextural data
    if (siteID == 'RU003') | (siteID == 'RU004'):
        #plot lmwl line
        lmwl = pd.read_csv('isotopes_supplementary/isoplot_lmwl_fit.csv')
        plt.plot(lmwl['delta18O'], lmwl['D'], color='black', label='LMWL', marker='None')
        #plot local sampled meteoric waters
        localmw = pd.read_csv('isotopes_supplementary/Rainwater_isotopes.csv')
        plt.plot(localmw['delta18O'], localmw['D'], color='green', label='local meteoric', marker='o', linestyle='None')
        #plot volcanic arc region
        volcarc = pd.read_csv('isotopes_supplementary/VolcanicArc_isotopes.csv')
        plt.plot(volcarc['delta18O'], volcarc['D'], color='red', marker='None', label='_nolegend_')
        #and label
        plt.text(9,-20,'volcanic arc',ha='center')
        #plot 'by eye' mixing line for these data, as developed by Agnes Mazot
        plt.plot([-9.7,9],[-62,-8], color='black', label='mixing line', marker='None', linestyle=':')
    elif (siteID== 'WI201'):
        #plot lmwl line
        lmwl = pd.read_csv('isotopes_supplementary/isoplot_lmwl_fit.csv')
        plt.plot(lmwl['delta18O'], lmwl['D'], color='black', label='LMWL', marker='None')
        #plot local sampled sea water
        localsw = pd.read_csv('isotopes_supplementary/SeaWater_isotopes_whiteisland.csv')
        plt.plot(localsw['delta18O'], localsw['D'], color='blue', label='local sea water', marker='o', linestyle='None')
        #plot local sampled meteoric water
        localmw = pd.read_csv('isotopes_supplementary/MeteoricWaters_isotopes_whiteisland.csv')
        plt.plot(localmw['delta18O'], localmw['D'], color='green', label='local meteoric', marker='o', linestyle='None')
        #plot volcanic arc region
        volcarc = pd.read_csv('isotopes_supplementary/VolcanicArc_isotopes.csv')
        plt.plot(volcarc['delta18O'], volcarc['D'], color='red', marker='None', label='_nolegend_')
        #and label
        plt.text(9,-20,'volcanic arc',ha='center')
        #plot 'by eye' mixing line for these data, as developed by Agnes Mazot
        plt.plot([-5,11.5],[-22,24], color='black', label='mixing line', marker='None', linestyle=':')
    elif (siteID== 'OT001'):
        #plot lmwl line
        lmwl = pd.read_csv('isotopes_supplementary/isoplot_lmwl_fit.csv')
        plt.plot(lmwl['delta18O'], lmwl['D'], color='black', label='LMWL', marker='None')
        #plot local sampled meteoric water
        localmw = pd.read_csv('isotopes_supplementary/MeteoricWaters_isotopes_waimangu.csv')
        plt.plot(localmw['delta18O'], localmw['D'], color='green', label='local meteoric', marker='o', linestyle='None')
        #plot volcanic arc region
        volcarc = pd.read_csv('isotopes_supplementary/VolcanicArc_isotopes.csv')
        plt.plot(volcarc['delta18O'], volcarc['D'], color='red', marker='None', label='_nolegend_')
        #and label
        plt.text(9,-20,'volcanic arc',ha='center')
    elif (siteID== 'OT002'):
        #plot lmwl line
        lmwl = pd.read_csv('isotopes_supplementary/isoplot_lmwl_fit.csv')
        plt.plot(lmwl['delta18O'], lmwl['D'], color='black', label='LMWL', marker='None')
        #plot local sampled meteoric water
        localmw = pd.read_csv('isotopes_supplementary/MeteoricWaters_isotopes_waimangu.csv')
        plt.plot(localmw['delta18O'], localmw['D'], color='green', label='local meteoric', marker='o', linestyle='None')
        #plot volcanic arc region
        volcarc = pd.read_csv('isotopes_supplementary/VolcanicArc_isotopes.csv')
        plt.plot(volcarc['delta18O'], volcarc['D'], color='red', marker='None', label='_nolegend_')
        #and label
        plt.text(9,-20,'volcanic arc',ha='center')

    # label
    plt.xlabel('18O (per mil)')
    plt.ylabel('2H (per mil)')

    #limits, dependent on siteID
    if (siteID == 'RU003') | (siteID == 'RU004'):
        plt.xlim(-12,12)
        plt.ylim(-80,0)
    elif (siteID== 'WI201'):
        plt.xlim(-10,20)
        plt.ylim(-50,60) 
    elif (siteID== 'OT001'):
        plt.xlim(-10,15)
        plt.ylim(-40,0) 
    elif (siteID== 'OT002'):
        plt.xlim(-10,15)
        plt.ylim(-40,0) 

    title = (sitename + ' (' + siteID + ') : isotope data, last observation: ' + strlast)
    plt.legend(loc='upper left', scatterpoints=1)
    plt.title(title)

    # save plot
    image = os.path.join(plotdir, 'isotope_'+siteID+'.png')
    plt.savefig(image, dpi=200)
