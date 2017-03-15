#!/usr/bin/env python
# compbaselines_geonet.py
#
# Compute and plot baselines lengths changes for stations pairs and produce images for volcano development webpage
# To run as a daily cron job
#
# Data are from FITS, daily average
# Usage: compbaselines.py config_file

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import requests
import pyproj
import scipy.signal
import sys
import os
import datetime
import ConfigParser
import numpy as np
from subprocess import call

# coordinate conversion lat-lon to nzmg


def deg2nzmg(lon, lat):
    # define projections
    proj_wgs84 = pyproj.Proj(init="epsg:4326")
    proj_nzmg = pyproj.Proj(init="epsg:27200")
    # convert coordinates from deg to NZMG
    e, n = pyproj.transform(proj_wgs84, proj_nzmg, lon, lat)
    # return Easting and Northing in NZMG
    return e, n

# input argument - configuration file
if (len(sys.argv) != 2):
    sys.exit("syntax compbaselines_geonet.py config_file")
else:
    cfg = sys.argv[1]

# parse configuration file
config = ConfigParser.ConfigParser()
config.read(cfg)
server = config.get('web', 'server')
user = config.get('web', 'user')
webdir = config.get('web', 'webdir')
kernel = int(config.get('process', 'kernel'))
xsize = float(config.get('plot', 'xsize'))
ysize = float(config.get('plot', 'ysize'))
plot_dir = config.get('plot', 'plot_dir')
# get
days = config.items('days')
# get region names
regions = []
for section in config.sections():
    if 'lines-' in section:
        reg = section.split('-')[1]
        regions.append(reg)

# loop through regions
for reg in regions:
    print 'region = ', reg
    str = 'lines-' + reg
    lines = config.items('lines-' + reg)
    nlines = len(lines)
    print 'nlines = ', nlines

    # loop through plot durations
    for id, day in days:
        print 'days = ', day

        # plot for this region
        fig = plt.figure(figsize=(xsize, ysize * nlines))

        # loop through lines
        for idx, line in enumerate(lines):
            site1 = line[1].split()[0]
            site2 = line[1].split()[1]
            siteid1 = site1.split('.')[0]
            netid1 = site1.split('.')[1]
            siteid2 = site2.split('.')[0]
            netid2 = site2.split('.')[1]
            print '  plot = ', idx + 1, siteid1, netid1, siteid2, netid2

            # get position data for sites, FITS query
            # first site
            url = 'http://fits.geonet.org.nz/site'
            payload = {'siteID': siteid1, 'networkID': netid1}
            r = requests.get(url, params=payload)
            # get from a dictionary
            jdata = r.json()
            lon = jdata.values()[1][0]['geometry']['coordinates'][0]
            lat = jdata.values()[1][0]['geometry']['coordinates'][1]
            pos_e, pos_n = deg2nzmg(lon, lat)
            # print 'coordinates ', siteid1, pos_e, pos_n
            pos_z = jdata.values()[1][0]['properties']['height']
            # convert to mm
            pos_e *= 1000
            pos_n *= 1000
            pos_z *= 1000
            pos_e1 = pos_e
            pos_n1 = pos_n
            pos_z1 = pos_z
            # second site
            url = 'http://fits.geonet.org.nz/site'
            payload = {'siteID': siteid2, 'networkID': netid2}
            r = requests.get(url, params=payload)
            # get from a dictionary
            jdata = r.json()
            lon = jdata.values()[1][0]['geometry']['coordinates'][0]
            lat = jdata.values()[1][0]['geometry']['coordinates'][1]
            pos_e, pos_n = deg2nzmg(lon, lat)
            pos_z = jdata.values()[1][0]['properties']['height']
            # convert to mm
            pos_e *= 1000
            pos_n *= 1000
            pos_z *= 1000
            pos_e2 = pos_e
            pos_n2 = pos_n
            pos_z2 = pos_z

            # distance between sites (km)
            dist = ((pos_e1 - pos_e2)**2 + (pos_n1 - pos_n2)**2)**0.5
            dist /= 1e6
            str_dist = "%.2f" % dist

            # get time series data for sites, FITS query
            names = ['dt', 'obs', 'err']
            # first site
            url = 'http://fits.geonet.org.nz/observation?typeID=e&siteID=' + \
                siteid1 + '&networkID=' + netid1 + '&days=' + day
            df1e = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
            url = 'http://fits.geonet.org.nz/observation?typeID=n&siteID=' + \
                siteid1 + '&networkID=' + netid1 + '&days=' + day
            df1n = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
            url = 'http://fits.geonet.org.nz/observation?typeID=u&siteID=' + \
                siteid1 + '&networkID=' + netid1 + '&days=' + day
            df1u = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
            # second site
            url = 'http://fits.geonet.org.nz/observation?typeID=e&siteID=' + \
                siteid2 + '&networkID=' + netid2 + '&days=' + day
            df2e = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
            url = 'http://fits.geonet.org.nz/observation?typeID=n&siteID=' + \
                siteid2 + '&networkID=' + netid2 + '&days=' + day
            df2n = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})
            url = 'http://fits.geonet.org.nz/observation?typeID=u&siteID=' + \
                siteid2 + '&networkID=' + netid2 + '&days=' + day
            df2u = pd.read_csv(
                url, names=names, skiprows=1, parse_dates={"Datetime": ['dt']})

            # use only Datetimes common to both sites
            df1ea = df1e[df1e.Datetime.isin(df2e.Datetime)]
            df1na = df1n[df1n.Datetime.isin(df2n.Datetime)]
            df1ua = df1u[df1u.Datetime.isin(df2u.Datetime)]
            df2ea = df2e[df2e.Datetime.isin(df1e.Datetime)]
            df2na = df2n[df2n.Datetime.isin(df1n.Datetime)]
            df2ua = df2u[df2u.Datetime.isin(df1u.Datetime)]

            # reset indices
            df1ea = df1ea.reset_index(drop=True)
            df1na = df1na.reset_index(drop=True)
            df1ua = df1ua.reset_index(drop=True)
            df2ea = df2ea.reset_index(drop=True)
            df2na = df2na.reset_index(drop=True)
            df2ua = df2ua.reset_index(drop=True)

            # join dataframes, rename columns
            df = pd.concat(
                [df1ea, df1na, df1ua, df2ea, df2na, df2ua], axis=1, join='inner')
            names = ['Datetime', 'obse1', 'erre1', 'dtn1', 'obsn1', 'errn1', 'dtu1', 'obsu1',
                     'erru1', 'dte2', 'obse2', 'erre2', 'dtn2', 'obsn2', 'errn2', 'dtu2', 'obsu2', 'erru2']
            df.columns = names  # rename columns
            # df.drop(['dtn1','dte2','dtn2'], axis=1, inplace=True)  #drop
            # columns

            # add positions
            df['obse1'] = df['obse1'] + pos_e1
            df['obsn1'] = df['obsn1'] + pos_n1
            df['obsu1'] = df['obsu1'] + pos_z1
            df['obse2'] = df['obse2'] + pos_e2
            df['obsn2'] = df['obsn2'] + pos_n2
            df['obsu2'] = df['obsu2'] + pos_z2

            # pre-filter observations
            df['obse1f'] = scipy.signal.medfilt(df['obse1'], kernel)
            df['obsn1f'] = scipy.signal.medfilt(df['obsn1'], kernel)
            df['obsu1f'] = scipy.signal.medfilt(df['obsu1'], kernel)
            df['obse2f'] = scipy.signal.medfilt(df['obse2'], kernel)
            df['obsn2f'] = scipy.signal.medfilt(df['obsn2'], kernel)
            df['obsu2f'] = scipy.signal.medfilt(df['obsu2'], kernel)

            # line lengths, 3D
            df['le'] = df['obse1'] - df['obse2']
            df['ln'] = df['obsn1'] - df['obsn2']
            df['lu'] = df['obsu1'] - df['obsu2']
            df['xyz'] = np.sqrt(
                np.square(df['le']) + np.square(df['ln']) + np.square(df['lu']))

            # reference observations to first value
            df['xyz'] = df['xyz'] - df['xyz'][0]

            # filter line lengths
            df['xyzf'] = scipy.signal.medfilt(df['xyz'], kernel)

            # plot for this line
            # Set ticks interval and format for plot of all data
            majorTick = mpl.dates.YearLocator(1)
            majorFormat = mpl.dates.DateFormatter('%Y')
            minorTick = mpl.dates.MonthLocator(interval=1)

            if idx == 0:  # first plot for region
                fig.subplots_adjust(hspace=0.15)
                ax = fig.add_subplot(nlines, 1, idx + 1)
                plt.grid(
                    b=True, which='major', color='b', linestyle='--', alpha=0.5)
                plt.plot(
                    df['Datetime'], df['xyz'], marker='o', color='black', linestyle='None')
                plt.plot(
                    df['Datetime'], df['xyzf'], marker='None', color='red')
                plt.ylabel(siteid1 + ' - ' + siteid2)
                if day == '365000':  # all data
                    ax.xaxis.set_major_locator(majorTick)
                    ax.xaxis.set_major_formatter(majorFormat)
                    ax.xaxis.set_minor_locator(minorTick)
                now = datetime.datetime.now()
                title = (reg.capitalize(
                ) + ' baselines length change (mm) plotted at: ' + now.strftime("%Y-%m-%d %H:%M"))
                plt.title(title)
            else:
                ax = fig.add_subplot(nlines, 1, idx + 1, sharex=ax)
                plt.grid(
                    b=True, which='major', color='b', linestyle='--', alpha=0.5)
                plt.plot(
                    df['Datetime'], df['xyz'], marker='o', color='black', linestyle='None')
                plt.plot(
                    df['Datetime'], df['xyzf'], marker='None', color='red')
                plt.ylabel(siteid1 + ' - ' + siteid2)
                if day == '365000':  # all data
                    ax.xaxis.set_major_locator(majorTick)
                    ax.xaxis.set_major_formatter(majorFormat)
                    ax.xaxis.set_minor_locator(minorTick)
        # save region plot
        if day == '365000':  # all data
            image = os.path.join(plot_dir, reg + '.png')
        else:
            image = os.path.join(plot_dir, reg + '_' + day + '.png')
        # print '  image file = ', image
        plt.savefig(image, dpi=200)
        # send image to web server
        cmdstr = '/usr/bin/scp ' + image + ' ' + \
            user + '@' + server + ':' + webdir
        call(cmdstr, shell=True)
