# FITS_plotting
Python plotting of volcano data from FITS

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


