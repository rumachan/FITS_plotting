# FITS_plotting
Python plotting of volcano data from FITS

## Contents

### basicdaymean
Plots the mean of all White Island S02 mini-DOAS fluxes, provided there are at least 5 observations a day. A day is the NZST day. These values are those traditionally presented by volcano-geochemists at volcano monitoring meetings.

_Relevant files_
- basicdaymean.py
- basicdaymean.cfg
![GitHub Logo](/readme_images/mdoas.daymean5.png)

### mdoasplot
Plots a box and whisker diagram for White Island S02 mini-DOAS fluxes for each day. Days are UTC. This is currently no used, having being superseded by `combiplot`.

_Relevant files_
- mdoasplot.py
- mdoasplot.cfg

### combiplot
Plots a box and whisker diagram for White Island S02 mini-DOAS fluxes for each day, plus the number observations per day for each of the four data types. Days are UTC. The plots are made for different lengths of time (days). This superseded `mdoasplot`.

_Relevant files_
- combiplot.py
- combiplot.cfg
![GitHub Logo](/readme_images/mdoas.allobs_30.png)

### cumsum
Plots the 10-day mean of White Island S02 mini-DOAS fluxes and the cumulative sum of those data. The purpose is to show low-term, low-frequency variations and show periods of consistently higher or lower (than mean) fluxes.

_Relevant files_
- cumsum.py
- cumsum.cfg
![GitHub Logo](/readme_images/mdoas.allobs_resample_10d.png)

### compbaselines
Plots GNSS baselines for station pairs within a volcanic centre. Plots are made for different lengths of time (days). Plots within a volcanic centre are grouped together.

_Relevant files_
- compbaselines_geonet.py
- compbaselines.cfg
![GitHub Logo](/readme_images/gps.bll.taranaki_100.png)

### ruapcombi
Plot a combination of monitoring parameters from Ruapehu.

_Relevant files_
- ruapcombi.py
- ruapcombi.cfg
![GitHub Logo](/readme_images/ruapehu.combi_365.png)

### isoplot
Plot water isotope data as a cross-plot.

_Relevant files_
- isoplot.py
- isoplot.cfg
- isotopes_supplementary/
![GitHub Logo](/readme_images/ruapehu.combi_365.png)

## Docker

To install and run the scripts in a docker image proceed as follows.

First get the source code:

```
git clone  --depth=1  https://github.com/rumachan/FITS_plotting.git
```

Then build and run the docker image using the `buildnrun.sh` script:

```
cd FITS_plotting
./buildnrun.sh -h
Usage: ./buildnrun.sh [Options]

Build and run docker image.

Options:
    -h              Show this message.
    -r              Only run image without rebuilding it.
    -b              Only rebuild image without running it.
    -t              Assign a tag to the docker image (default: latest).
```

By default `buildnrun.sh` runs both the build and run stage.

Using the `buildnrun.sh` script also requires two docker volumes to be present: `html` and `rsam`.
`rsam` contains the file `MAVZ.asc`, a timeseries of RSAM values extending over several years
which is required by the script `ruapcombi.py` and is produced by [ascii_daily.sh](https://github.com/rumachan/RSAM/blob/master/ascii_daily.sh). `html` stores the final plots.

To generate the `html` volume run:

```
docker volume create html
```


