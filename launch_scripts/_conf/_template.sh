#!/bin/bash

set -e

cd _WORK_DIR_

# Compute:
################################################################################
mpirun -np 3 _EXECUTABLE_FOLDER_/_PDE_ _ARGS_ \
  --dim=_DIM_\
  --prm=_PRMNAME_ | tee _OUTPUT_LOG_FILE_

# Post processing:
################################################################################
CHECK=`ls *vtu 2>/dev/null`
if [[ ! -z ${CHECK} ]] 
then
  mkdir _IMAGES_DIR_
  mv *vtu _IMAGES_DIR_
fi

# End:
################################################################################
touch "__JOB_COMPLETED__"