#!/bin/bash

__PBS__

set -e

cd __WORK_DIR__

# Compute:
################################################################################
mpirun __MPIRUN_FLAGS__ \
  __EXECUTABLE__ \
  __ARGS__ \
  2>>__ERROR_LOG_FILE__
  | -a tee __OUTPUT_LOG_FILE__

# End:
################################################################################
touch "__JOB_COMPLETED__"