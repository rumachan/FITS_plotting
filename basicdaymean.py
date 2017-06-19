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
  sys.exit('syntax basicdaymean.py config_file')
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
minobs = int(config.get('obs','minobs'))
tzone = config.get('tzone', 'tzone')

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

#determine number of plots
nplots = len(days) + 1

###daily mean, when nobs >= minobs###

id, day = days[0]
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

#sort by datetime and reindex
df.sort_values('Datetime', inplace=True)  
df.reset_index(inplace=True)

#tzone, ut or nzst
if (tzone=='nzst'):
  df['Datetime'] = df['Datetime'] + pd.to_timedelta(12, unit='h')  

#number obs per day
dfcount = df['obs'].groupby(df['Datetime'].dt.date).count()

#determine condtion, groupby, select based on condition (messy)
dfcond = (dfcount >= minobs)
dfm = df['obs'].groupby(df['Datetime'].dt.date).mean()
dfmean = pd.concat([dfm, dfcond], axis = 1)
dfmean = dfmean[:len(dfcond)]
dfmean.columns = ['obs', 'cond']
dfmean = dfmean[dfmean['cond'] == True]
dfmean.index = pd.to_datetime(dfmean.index)

#plot
fig, ax1 = plt.subplots(figsize=(xsize, ysize))
ax1.plot(dfmean.index, dfmean['obs'], marker='o', markersize=5, color='red', linestyle='None')
ax1.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
ax1.set_ylabel('SO2 flux ('+unit+')')
#alternate y-axis
ax2 = ax1.twinx()
y1, y2=ax1.get_ylim()
ax2.set_ylim(y1*kgs2tpd, y2*kgs2tpd)
dftpd = dfmean['obs'] * kgs2tpd
ax2.plot(dfmean.index, dftpd, marker='o', markersize=5, color='red', linestyle='None')
ax2.tick_params(axis='y', colors='gray')
ax2.set_ylabel('SO2 flux ('+unit2+')', color = 'gray')
if (tzone=='nzst'):
  plt.title('All observations: daily(NZST) mean (nobs>='+str(minobs)+')')
else:
  plt.title('All observations: daily(UT) mean (nobs>='+str(minobs)+')')
#save plot
image = os.path.join(plotdir, 'daymean'+str(minobs)+'.png')
plt.savefig(image, dpi=200)
cmdstr = '/usr/bin/scp '+ image + ' ' +webuser +'@' + webserver + ':' + webdir
call(cmdstr, shell=True)
