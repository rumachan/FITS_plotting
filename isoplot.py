#!/usr/bin/env python
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

# figure set up
fig = plt.figure(figsize=(xsize, ysize))

# site1
siteID = site1.split()[0].split('.')[0]
networkID = site1.split()[0].split('.')[1]
typeID = site1.split()[1]

# site1 meta data
url = 'http://fits.geonet.org.nz/site'
payload = {'siteID': siteID, 'networkID': networkID}
r = requests.get(url, params=payload)
jdata = r.json()
sitename = jdata.values()[1][0]['properties']['name'].encode('ascii', 'ignore')

# time series data and plot
ax = fig.add_subplot(1, 2, 1)
url = 'https://fits.geonet.org.nz/observation?typeID=' + \
    typeID + '&siteID=' + siteID + '&networkID=' + networkID
dfo = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
# meta data for lat observation
url = 'http://fits.geonet.org.nz/observation/stats'
payload = {'typeID': typeID, 'siteID': siteID, 'networkID': networkID}
r = requests.get(url, params=payload)
jdata = r.json()
last = jdata.get('Last').get('DateTime').encode('ascii', 'ignore')
dtlast = parser.parse(last)
strlast = dtlast.strftime("%Y-%m-%d")
# site1 2nd data set
typeID = site1.split()[2]
url = 'https://fits.geonet.org.nz/observation?typeID=' + \
    typeID + '&siteID=' + siteID + '&networkID=' + networkID
dfh = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

# plot data for site1
plt.scatter(dfo['obs'], dfh['obs'], marker='o',
            color='black', label='all data')
# plot recent data
plt.plot(dfo['obs'][-5:], dfh['obs'][-5:], color='red', linewidth=2)
plt.scatter(dfo['obs'][-5:], dfh['obs'][-5:],
            color='red', s=100, label='recent data')
plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='red', s=200)  # last
plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='black',
            s=200, marker='*', label='last data')  # last
# label
plt.xlabel('18O (per mil)')
plt.ylabel('2H (per mil)')
title = (sitename + ' (' + siteID + ') : isotope data, last value: ' + strlast)
plt.legend(loc='upper left', scatterpoints=1)
plt.title(title)

# site2
siteID = site2.split()[0].split('.')[0]
networkID = site2.split()[0].split('.')[1]
typeID = site2.split()[1]

ax = fig.add_subplot(1, 2, 2)
# site meta data
url = 'http://fits.geonet.org.nz/site'
payload = {'siteID': siteID, 'networkID': networkID}
r = requests.get(url, params=payload)
jdata = r.json()
sitename = jdata.values()[1][0]['properties']['name'].encode('ascii', 'ignore')

# time series data and plot
url = 'https://fits.geonet.org.nz/observation?typeID=' + \
    typeID + '&siteID=' + siteID + '&networkID=' + networkID
dfo = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
# meta data for lat observation
url = 'http://fits.geonet.org.nz/observation/stats'
payload = {'typeID': typeID, 'siteID': siteID, 'networkID': networkID}
r = requests.get(url, params=payload)
jdata = r.json()
last = jdata.get('Last').get('DateTime').encode('ascii', 'ignore')
dtlast = parser.parse(last)
strlast = dtlast.strftime("%Y-%m-%d")
url = 'https://fits.geonet.org.nz/observation?typeID=' + \
    typeID + '&siteID=' + siteID + '&networkID=' + networkID
dfo = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
# site2 2nd data set
typeID = site2.split()[2]
url = 'https://fits.geonet.org.nz/observation?typeID=' + \
    typeID + '&siteID=' + siteID + '&networkID=' + networkID
dfh = pd.read_csv(
    url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
# plot all data
plt.scatter(dfo['obs'], dfh['obs'], marker='o',
            color='black', label='all data')
# plot recent data
plt.plot(dfo['obs'][-5:], dfh['obs'][-5:], color='red', linewidth=2)
plt.scatter(dfo['obs'][-5:], dfh['obs'][-5:],
            color='red', s=100, label='recent data')
plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='red', s=200)  # last
plt.scatter(dfo['obs'][-1:], dfh['obs'][-1:], color='black',
            s=200, marker='*', label='last data')  # last

# label
plt.xlabel('18O (per mil)')
plt.ylabel('2H (per mil)')
strlast = dfo['Datetime'][-2:-1].dt.strftime('%Y-%m-%d').min()
plt.legend(loc='upper left', scatterpoints=1)
title = (sitename + ' (' + siteID + ') : isotope data, last value: ' + strlast)
plt.title(title)

# save plot
image = os.path.join(plotdir, 'ruapehu_isotope.png')
plt.savefig(image, dpi=200)
