# FITS_plotting
Python plotting of volcano data from FITS

## Docker

First get the source code:

```
git clone  --depth=1  https://github.com/rumachan/FITS_plotting.git
```
Then build the docker image:

```
cd FITS_plotting
docker build -t fitsplots .
```
The resulting docker image has two mount points that have to be mounted
so the scripts can run:

* `/home/volcano/workdir`: contains the file `MAVZ.asc`, a timeseries of RSAM values extending over several years which is required by the script `ruapcombi.py` and
is produced by [ascii_daily.sh](https://github.com/rumachan/RSAM/blob/master/ascii_daily.sh)
* `/home/volcano/output`: stores output files for the website

Let's assume the following setup:

|Contents                  |Host directory                | Container directory |
|--------------------------|------------------------------|---------------------|
|Persistent work directory |/home/volcano/rsam_work/      |/home/volcano/workdir|
|Output for web server     |/var/www/html/geonet_wiki_data|/home/volcano/output |

Then you can create a container and run, for example, the `run_all.sh` script (which in turn runs all the Python scripts) for the first time as follows:

```
docker run --name fitsplots -it
-v /var/www/html/geonet_wiki_data:/home/volcano/output \
-v /home/volcano/rsam_work:/home/volcano/workdir  fitsplots run_all.sh
```
Afterwards you will only have to start the container `fitsplots` to rerun `run_all.sh`:
```
docker start fitsplots
```
In the same way you can create containers for the Python scripts.
