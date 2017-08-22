#!/bin/bash

#####################################
# Run all scripts in sequence       #
# 03/17 Y. Behr <y.behr@gns.cri.nz> #
#####################################

basicdaymean.py basicdaymean.cfg

combiplot.py combiplot.cfg

compbaselines_geonet.py compbaselines.cfg

cumsum.py cumsum.cfg

isoplot.py isoplot.cfg

mdoasplot.py mdoasplot.cfg

ruapcombi.py ruapcombi.cfg
