#!/bin/bash

set -e

# Source variables, compilers, and modules:
################################################################################
source "./_export.cfg"

# Configuration:
################################################################################
ARGS="--dim=2"
PRM="--prm=${NESSUS_DIR}/prm/navier_stokes/flow_past_a_cylinder_2D_00.prm"

# Compute:
################################################################################

cd ${NESSUS_DIR}
NEXT_DIR=`${GET_NEXT_DIR} -F ${BASE_FOLDER} -f ${RUN_FOLDER}`
mkdir ${NEXT_DIR}
cd ${NEXT_DIR}

mpirun -np 3 ${FLUID_DYNAMICS} ${ARGS} ${PRM} | tee ${OUTPUT_LOG_FILE}

mkdir ${IMAGES_DIR}
mv *vtu ${IMAGES_DIR}
