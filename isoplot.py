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
site1 = config.get('sites', 'site1')
site2 = config.get('sites', 'site2')

# site1
siteID = site1.split()[0]
typeID = site1.split()[1]

# site1 meta data
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
dfo = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

# meta data for last observation
url = 'http://fits.geonet.org.nz/observation/stats'
payload = {'typeID': typeID, 'siteID': siteID}
r = requests.get(url, params=payload)
jdata = r.json()
last = jdata.get('Last').get('DateTime').encode('ascii', 'ignore')
dtlast = parser.parse(last)
strlast = dtlast.strftime("%Y-%m-%d")

# site1 2nd data set
typeID = site1.split()[2]
url = 'https://fits.geonet.org.nz/observation?typeID=' +     typeID + '&siteID=' + siteID
dfh = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

# plot data for site1
plt.scatter(dfo['obs'], dfh['obs'], marker='o', color='black', label='all obs')
# plot recent data
# plt.plot(dfo['obs'][-5:], dfh['obs'][-5:], color='red', linewidth=2, label='_nolegend_')
# plt.scatter(dfo['obs'][-5:], dfh['obs'][-5:], color='red', s=100, label='recent data')
plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='red', s=100, label='last obs')  # last
# plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='black', s=200, marker='*', label='last obs')  # last
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


# label
plt.xlabel('18O (per mil)')
plt.ylabel('2H (per mil)')

#limits
plt.xlim(-12,12)
plt.ylim(-80,0)

title = (sitename + ' (' + siteID + ') : isotope data, last observation: ' + strlast)
plt.legend(loc='upper left', scatterpoints=1)
plt.title(title)

# save plot
image = os.path.join(plotdir, 'ruapehu_isotope_'+siteID+'.png')
plt.savefig(image, dpi=200)


# site2
siteID = site2.split()[0]
typeID = site2.split()[1]

# site2 meta data
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
dfo = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

# meta data for last observation
url = 'http://fits.geonet.org.nz/observation/stats'
payload = {'typeID': typeID, 'siteID': siteID}
r = requests.get(url, params=payload)
jdata = r.json()
last = jdata.get('Last').get('DateTime').encode('ascii', 'ignore')
dtlast = parser.parse(last)
strlast = dtlast.strftime("%Y-%m-%d")

# site2 2nd data set
typeID = site1.split()[2]
url = 'https://fits.geonet.org.nz/observation?typeID=' +     typeID + '&siteID=' + siteID
dfh = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

# plot data for site2
plt.scatter(dfo['obs'], dfh['obs'], marker='o', color='black', label='all obs')
# plot recent data
# plt.plot(dfo['obs'][-5:], dfh['obs'][-5:], color='red', linewidth=2, label='_nolegend_')
# plt.scatter(dfo['obs'][-5:], dfh['obs'][-5:], color='red', s=100, label='recent data')
plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='red', s=100, label='last obs')  # last
# plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='black', s=200, marker='*', label='last obs')  # last
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


# label
plt.xlabel('18O (per mil)')
plt.ylabel('2H (per mil)')

#limits
plt.xlim(-12,12)
plt.ylim(-80,0)

title = (sitename + ' (' + siteID + ') : isotope data, last observation: ' + strlast)
plt.legend(loc='upper left', scatterpoints=1)
plt.title(title)

# save plot
image = os.path.join(plotdir, 'ruapehu_isotope_'+siteID+'.png')
plt.savefig(image, dpi=200)

