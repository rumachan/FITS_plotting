#!/usr/bin/env python
import sys, os
import ConfigParser
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from subprocess import call

def getsite(site):
  siteID = site.split()[0].split('.')[0]
  networkID = site.split()[0].split('.')[1]
  typeID = site.split()[1]
  methodID = site.split()[2]
  return siteID, networkID, typeID, methodID

names = ['dt', 'obs', 'err']
kgs2tpd = 86.4	#conversion kg/s to t/d

#configuration file
if (len(sys.argv) != 2):
  sys.exit('syntax combiplot.py config_file')
else:
  cfg = sys.argv[1]

#parse configuration file
config = ConfigParser.ConfigParser()
config.read(cfg)
webserver = config.get('web','server')
webuser = config.get('web','user')
webdir = config.get('web','dir')
xsize = float(config.get('plot','xsize'))
ysize = float(config.get('plot','ysize'))
ymax = float(config.get('plot','ymax'))
plotdir = config.get('plot','dir')
days = config.items('days')

#sites
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

#loop through plot durations
for id, day in days:
  #site1   
  url= 'https://fits.geonet.org.nz/observation?typeID='+typeID1+'&methodID='+methodID1+'&siteID='+siteID1+'&networkID='+networkID1+'&days='+day
  df1 = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime" : ['dt']})
  #site2   
  url= 'https://fits.geonet.org.nz/observation?typeID='+typeID2+'&methodID='+methodID2+'&siteID='+siteID2+'&networkID='+networkID2+'&days='+day
  df2 = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime" : ['dt']})
  #site3   
  url= 'https://fits.geonet.org.nz/observation?typeID='+typeID3+'&methodID='+methodID3+'&siteID='+siteID3+'&networkID='+networkID3+'&days='+day
  df3 = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime" : ['dt']})
  #site4   
  url= 'https://fits.geonet.org.nz/observation?typeID='+typeID4+'&methodID='+methodID4+'&siteID='+siteID4+'&networkID='+networkID4+'&days='+day
  df4 = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime" : ['dt']})

  #concatenate dataframes
  frames = [df1, df2, df3, df4]
  df = pd.concat(frames)

  fig, ax1 = plt.subplots(figsize=(xsize, ysize))

  #sort by datetime and reindex
  df.sort_values('Datetime', inplace=True)  
  df.reset_index(inplace=True)

  #number obs per day
  dfcount = df['obs'].groupby(df['Datetime'].dt.date).count()
  dfcount.index = pd.to_datetime(dfcount.index)

  #min/max obs per day
  dfmin = df['obs'].groupby(df['Datetime'].dt.date).min()
  dfmax = df['obs'].groupby(df['Datetime'].dt.date).max()
  dfcount.index = pd.to_datetime(dfcount.index)
  ax1.bar(dfcount.index, dfmax-dfmin, bottom=dfmin, width=0.01, color='black', edgecolor='black', alpha=0.25, align='center', label='range')

  #mean per day
  dfmean = df['obs'].groupby(df['Datetime'].dt.date).mean()
  ax1.plot(dfcount.index, dfmean, marker='o', markersize=3, color='red', linestyle='None', label='mean')
    #alternate y-axis
  ax2 = ax1.twinx()
  y1, y2=ax1.get_ylim()
  ax2.set_ylim(0, ymax*kgs2tpd)
  dftpd = dfmean * kgs2tpd
  ax2.plot(dfcount.index, dftpd, marker='o', markersize=3, color='red', linestyle='None', label='mean')

  #25th and 75th percentile
  dfup = df['obs'].groupby(df['Datetime'].dt.date).quantile(0.75)
  dflp = df['obs'].groupby(df['Datetime'].dt.date).quantile(0.25)
  ax1.bar(dfcount.index, dfup-dflp, bottom=dflp, width=0.1, color='blue', edgecolor='blue', align='center', label='25th/75th %')

  ax1.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
  ax1.set_ylabel('SO2 flux ('+unit+')')
  ax2.set_ylabel('SO2 flux ('+unit2+')', color = 'gray')
  ax2.tick_params(axis='y', colors='gray')
  ax1.legend(loc='upper left')
  ax1.set_ylim([0,ymax])
  plt.title('All observations')
#save plot
  if day == '365000':  #all data
    image = os.path.join(plotdir, 'allobs.png')
  else:
    image = os.path.join(plotdir, 'allobs_'+day+'.png')
  #print '  image file = ', image
  plt.savefig(image, dpi=200)
  cmdstr = '/usr/bin/scp '+ image + ' ' +webuser +'@' + webserver + ':' + webdir
  call(cmdstr, shell=True)
