#!/usr/bin/env python
import matplotlib
matplotlib.use('Agg')
import sys
import os
import ConfigParser
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
import requests


def getsite(site):
    siteID = site[1].split()[0].split('.')[0]
    networkID = site[1].split()[0].split('.')[1]
    typeID = site[1].split()[1]
    methodID = site[1].split()[2]
    return siteID, networkID, typeID, methodID


def getsitesingle(site):
    siteID = site.split()[0].split('.')[0]
    networkID = site.split()[0].split('.')[1]
    typeID = site.split()[1]
    methodID = site.split()[2]
    return siteID, networkID, typeID, methodID


def getsitename(site, network):
    url = 'http://fits.geonet.org.nz/site'
    payload = {'siteID': site, 'networkID': network}
    r = requests.get(url, params=payload)
    # get from a dictionary
    jdata = r.json()
    jdict = jdata['features'][0]
    sitename = jdict['properties']['name'].encode('ascii', 'ignore')
    return sitename

# set up data
names = ['dt', 'obs', 'err']
kgs2tpd = 86.4  # conversion kg/s to t/d
molrat = 1.4545
csratmax = 200
nplots = 5

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
plotdir = config.get('plot', 'dir')
days = config.items('days')
waterdata = config.items('waterdata')

# loop through water sites, download and plot
for nday, day in days:
    print day
    fig = plt.figure(figsize=(xsize, ysize * nplots))

    #***crater lake temperature***
    print '***temperature***'
    ax1 = fig.add_subplot(nplots, 1, 1)
    temp1 = config.get('temps', 'temp1')
    (siteID, networkID, typeID, methodID) = getsitesingle(temp1)
    print siteID, networkID, typeID, methodID
    sitename = getsitename(siteID, networkID)
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    plt.plot(df['Datetime'], df['obs'], marker='None',
             color='red', linewidth=2, label=sitename)

    temp2 = config.get('temps', 'temp2')
    (siteID, networkID, typeID, methodID) = getsitesingle(temp2)
    print siteID, networkID, typeID, methodID
    sitename = getsitename(siteID, networkID)
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    plt.plot(df['Datetime'], df['obs'], marker='o', markersize=10,
             color='green', linewidth=2, label=sitename)

    temp3 = config.get('temps', 'temp3')
    (siteID, networkID, typeID, methodID) = getsitesingle(temp3)
    print siteID, networkID, typeID, methodID
    sitename = getsitename(siteID, networkID)
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    plt.plot(df['Datetime'], df['obs'], marker='o', markersize=10,
             color='blue', linewidth=2, label=sitename)
    ax1.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
    plt.ylabel('temperature (deg C)')
    plt.legend(loc='best', fontsize=10)
    x1, x2 = ax1.get_xlim()

    #***TDS***
    print '***TDS***'
    ax2 = fig.add_subplot(nplots, 1, 2, sharex=ax1)
    for (n, water) in enumerate(waterdata):
        (siteID, networkID, typeID, methodID) = getsite(water)
        print n, siteID, networkID, typeID, methodID
        url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
            siteID + '&networkID=' + networkID + \
            '&methodID=' + methodID + '&days=' + day
        if (n == 0):
            dftds = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
        else:
            df = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
            dftds['obs'] = dftds['obs'] + df['obs']

    ax2.plot(dftds['Datetime'], dftds['obs'], marker='o',
             markersize=10, color='red', linewidth=2, label='TDS')
    ax2.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
    plt.ylabel('total dissolved solids-TDS (mg/L)')
    ax2.legend(loc='best', fontsize=10)

    #***Mg/Cl on same plot***
    print '***Mg/Cl***'
    # alternate y-axis
    ax2a = ax2.twinx()
    mg = config.get('mgcl', 'mg')
    (siteID, networkID, typeID, methodID) = getsitesingle(mg)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    dfmg = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    cl = config.get('mgcl', 'cl')
    (siteID, networkID, typeID, methodID) = getsitesingle(cl)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    dfcl = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    mg = dfmg[dfmg.Datetime.isin(dfcl.Datetime)]
    cl = dfcl[dfcl.Datetime.isin(dfmg.Datetime)]
    mg = mg.reset_index(drop=True)
    cl = cl.reset_index(drop=True)
    dfmgcl = mg['obs'] / cl['obs']
    dfmgcl[np.isinf(dfmgcl)] = np.nan
    ax2a.plot(mg['Datetime'], dfmgcl, marker='o', markersize=10,
              color='blue', linewidth=2, label='Mg/Cl')
    ax2a.tick_params(axis='y', colors='blue')
    ax2a.set_ylabel('Mg/Cl ratio', color='blue')

    ax2a.legend(loc='lower right', fontsize=10)

    #***airborne gas flux***
    print '***gas flux***'
    ax3 = fig.add_subplot(nplots, 1, 3, sharex=ax1)
    gas1 = config.get('gases', 'gas1')
    (siteID, networkID, typeID, methodID) = getsitesingle(gas1)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    plt.plot(df['Datetime'], df['obs'], marker='o', markersize=10,
             color='red', linewidth=2, label=typeID + ' ' + methodID)

    gas2 = config.get('gases', 'gas2')
    (siteID, networkID, typeID, methodID) = getsitesingle(gas2)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    plt.plot(df['Datetime'], df['obs'], marker='^', markersize=10,
             color='red', linewidth=2, label=typeID + ' ' + methodID)

    # flyspec, returns no data
    #gas3 = config.get('gases', 'gas3')
    #(siteID, networkID, typeID, methodID) = getsitesingle(gas3)
    # print siteID, networkID, typeID, methodID
    #url= 'https://fits.geonet.org.nz/observation?typeID='+typeID+'&siteID='+siteID+'&networkID='+networkID+'&methodID='+methodID+'&days='+day
    #df = pd.read_csv(url, names=names, skiprows=1, parse_dates={"Datetime" : ['dt']})
    #plt.plot(df['Datetime'], df['obs'], marker='v', markersize=10, color = 'red', linewidth = 2, label = typeID+' '+methodID)

    gas4 = config.get('gases', 'gas4')
    (siteID, networkID, typeID, methodID) = getsitesingle(gas4)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    plt.plot(df['Datetime'], df['obs'], marker='o', markersize=10,
             color='green', linewidth=2, label=typeID + ' ' + methodID)

    gas5 = config.get('gases', 'gas5')
    (siteID, networkID, typeID, methodID) = getsitesingle(gas5)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    df = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
    # H2S very small, x 100 for plotting
    df['obs'] = df['obs'] * 100
    plt.plot(df['Datetime'], df['obs'], marker='o', markersize=10,
             color='blue', linewidth=2, label=typeID + ' ' + methodID + ' x 100')
    ax3.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
    plt.ylabel('gas flux (kg/s)')
    plt.legend(loc='best', fontsize=10)
    # alternate y-axis
    ax3a = ax3.twinx()
    y1, y2 = ax3.get_ylim()
    ax3a.set_ylim(y1 * kgs2tpd, y2 * kgs2tpd)
    dftpd = df['obs'] * kgs2tpd
    ax3a.plot(df['Datetime'], dftpd, marker='o',
              markersize=10, color='blue', linewidth=2)
    ax3a.tick_params(axis='y', colors='gray')
    ax3a.set_ylabel('gas flux (t/d)', color='gray')

    #***molar ratio, CO2/SO2***
    print '***molar ratio***'
    ax4 = fig.add_subplot(nplots, 1, 4, sharex=ax1)

    so2cosp = config.get('molar', 'so2cosp')
    (siteID, networkID, typeID, methodID) = getsitesingle(so2cosp)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    dfso2cosp = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    so2cont = config.get('molar', 'so2cont')
    (siteID, networkID, typeID, methodID) = getsitesingle(so2cont)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    dfso2cont = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    co2cont = config.get('molar', 'co2cont')
    (siteID, networkID, typeID, methodID) = getsitesingle(co2cont)
    print siteID, networkID, typeID, methodID
    url = 'https://fits.geonet.org.nz/observation?typeID=' + typeID + '&siteID=' + \
        siteID + '&networkID=' + networkID + \
        '&methodID=' + methodID + '&days=' + day
    dfco2cont = pd.read_csv(
        url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

    # make sure we have only common Datetimes in each ratio pair
    co2cont = dfco2cont[dfco2cont.Datetime.isin(dfso2cosp.Datetime)]
    so2cosp = dfso2cosp[dfso2cosp.Datetime.isin(dfco2cont.Datetime)]
    co2cont = co2cont.reset_index(drop=True)
    so2cosp = so2cosp.reset_index(drop=True)
    dfratcosp = co2cont['obs'] / so2cosp['obs'] * molrat
    dfratcosp[np.isinf(dfratcosp)] = np.nan
    plt.plot(so2cosp['Datetime'], dfratcosp, marker='o',
             markersize=10, color='red', linewidth=2, label='CO2/SO2-cosp')

    co2cont = dfco2cont[dfco2cont.Datetime.isin(dfso2cont.Datetime)]
    so2cont = dfso2cont[dfso2cont.Datetime.isin(dfco2cont.Datetime)]
    co2cont = co2cont.reset_index(drop=True)
    so2cont = so2cont.reset_index(drop=True)
    dfratcont = co2cont['obs'] / so2cont['obs'] * molrat
    dfratcont[np.isinf(dfratcont)] = np.nan
    plt.plot(so2cont['Datetime'], dfratcont, marker='o',
             markersize=10, color='blue', linewidth=2, label='CO2/SO2-cont')
    ax4.set_ylim(0, csratmax)
    ax4.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
    plt.ylabel('molar ratio')
    plt.legend(loc='best', fontsize=10)

    #***RSAM***
    print '***rsam***'
    ax5 = fig.add_subplot(nplots, 1, 5, sharex=ax1)

    rsamnames = ['dt', 'obs']
    rsamfile = config.get('rsam', 'file')
    dfrsam = pd.read_csv(
        rsamfile, names=rsamnames, delim_whitespace=True, parse_dates={"Datetime": ['dt']})
    # some values = -1??? and cut time to x-axis start time
    x1dt = dates.num2date(x1)
    #plot = dfrsam[(dfrsam['obs']>0)]
    plot = dfrsam[(dfrsam['obs'] > 0) & (dfrsam['Datetime'] > x1dt)]
    plt.plot(plot['Datetime'], plot['obs'], marker='None',
             color='red', linewidth=2, label='RSAM')
    ax5.grid(b=True, which='major', color='b', linestyle='--', alpha=0.5)
    ax5.set_xlim(x1, x2)
    plt.ylabel('ground velocity (nm/s)')
    plt.legend(loc='best', fontsize=10)

    # save plot
    if day == '365000':  # all data
        image = os.path.join(plotdir, 'combi.png')
    else:
        image = os.path.join(plotdir, 'ruapehu.combi_' + day + '.png')
    plt.savefig(image, dpi=200)
