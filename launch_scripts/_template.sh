#!/bin/bash

set -e

# Source variables, compilers, and modules:
################################################################################
source "./_export.cfg"

# Configuration:
################################################################################
ARGS="--dim=2"
PRM="${NESSUS_DIR}/prm/navier_stokes/flow_past_a_cylinder_2D_00.prm"

# Parameters
################################################################################
# viscosity:
nu=0.1
# number of refinemens:
ref=7
# stepper (euler|ida):
stepper=euler

# Compute:
################################################################################

cd ${NESSUS_DIR}
NEXT_DIR=`${GET_NEXT_DIR} -F ${BASE_FOLDER} -f ${RUN_FOLDER}`
mkdir ${NEXT_DIR}
cd ${NEXT_DIR}

PRM_USED="parameters.prm"
cp ${PRM} ${PRM_USED}

${FIND_AND_REPLACE} "_NU_" ${nu} ${PRM_USED}
${FIND_AND_REPLACE} "_REF_" ${ref} ${PRM_USED}
${FIND_AND_REPLACE} "_STEPPER_" ${stepper} ${PRM_USED}

mpirun -np 3 ${FLUID_DYNAMICS} ${ARGS} \
  "--prm=${PRM_USED}" | tee ${OUTPUT_LOG_FILE}

mkdir ${IMAGES_DIR}
mv *vtu ${IMAGES_DIR}
