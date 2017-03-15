#!/usr/bin/env python
import sys
import os
import ConfigParser
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests


def getsite(site):
    siteID = site.split()[0].split('.')[0]
    networkID = site.split()[0].split('.')[1]
    typeID = site.split()[1]
    methodID = site.split()[2]
    return siteID, networkID, typeID, methodID

names = ['dt', 'obs', 'err']
kgs2tpd = 86.4  # conversion kg/s to t/d

# configuration file
if (len(sys.argv) != 2):
    sys.exit('syntax combiplot.py config_file')
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
rs = config.get('resample', 'rs')

# sites
site1 = config.get('sites', 'site1')
(siteID1, networkID1, typeID1, methodID1) = getsite(site1)
site2 = config.get('sites', 'site2')
(siteID2, networkID2, typeID2, methodID2) = getsite(site2)
site3 = config.get('sites', 'site3')
(siteID3, networkID3, typeID3, methodID3) = getsite(site3)
site4 = config.get('sites', 'site4')
(siteID4, networkID4, typeID4, methodID4) = getsite(site4)

unit = 'kg/s'
unit2 = 't/d'

# site1
url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID1 + \
    '&methodID=' + methodID1 + '&siteID=' + \
    siteID1 + '&networkID=' + networkID1
df1 = pd.read_csv(
    url, names=names, skiprows=1, index_col=0, parse_dates={"Datetime": ['dt']})
# site2
url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID2 + \
    '&methodID=' + methodID2 + '&siteID=' + \
    siteID2 + '&networkID=' + networkID2
df2 = pd.read_csv(
    url, names=names, skiprows=1, index_col=0, parse_dates={"Datetime": ['dt']})
# site3
url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID3 + \
    '&methodID=' + methodID3 + '&siteID=' + \
    siteID3 + '&networkID=' + networkID3
df3 = pd.read_csv(
    url, names=names, skiprows=1, index_col=0, parse_dates={"Datetime": ['dt']})
# site4
url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID4 + \
    '&methodID=' + methodID4 + '&siteID=' + \
    siteID4 + '&networkID=' + networkID4
df4 = pd.read_csv(
    url, names=names, skiprows=1, index_col=0, parse_dates={"Datetime": ['dt']})

# concatenate dataframes
frames = [df1, df2, df3, df4]
df = pd.concat(frames)
# convert to t/d
df['obs'] = df['obs'] * kgs2tpd
df['err'] = df['err'] * kgs2tpd
# resample
dfrs = df.resample(rs)

fig, ax1 = plt.subplots(figsize=(xsize, ysize))

# mean obs per sample period
dfmean = dfrs['obs'].mean()
dfmean.index = pd.to_datetime(dfmean.index)
ax1.bar(dfmean.index, dfmean, width=3,
        color='red', edgecolor='red', align='edge')
ax1.set_ylabel('mean ' + rs + ' SO2 flux (t/d)', color='red')
ax1.tick_params(axis='y', colors='red')

dfcdf = (dfmean - dfmean.mean()).cumsum()
ax2 = ax1.twinx()
ax2.plot(dfmean.index, dfcdf, color='blue', linewidth=3)
ax2.set_ylabel('cumulative difference SO2 flux (t/d)', color='blue')
ax2.tick_params(axis='y', colors='blue')
mean = str(int(dfmean.mean()))
plt.title('All observations: resample = ' + rs +
          ', cumulative difference relative to mean (' + mean + ')')
# save plot
image = os.path.join(plotdir, 'allobs_resample_' + rs + '.png')
plt.savefig(image, dpi=200)
