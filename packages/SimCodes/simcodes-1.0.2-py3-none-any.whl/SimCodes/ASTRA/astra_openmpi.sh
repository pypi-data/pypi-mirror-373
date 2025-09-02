#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/OpenMPI-1.4.3/lib/:/opt/ASTRA/lib
/opt/ASTRA/astra_r62_Linux_x86_64_OpenMPI_sld6 $1
