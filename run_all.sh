#!/bin/bash

#####################################
# Run all scripts in sequence       #
# 03/17 Y. Behr <y.behr@gns.cri.nz> #
#####################################

basicdaymean.py scripts/basicdaymean.cfg

compbaselines_geonet.py scripts/compbaselines.cfg

cumsum.py scripts/cumsum.cfg

isoplot.py scripts/isoplot.cfg

mdoasplot.py scripts/mdoasplot.cfg

ruapcombi.py scripts/ruapcombi.cfg
