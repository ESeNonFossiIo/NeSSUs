#!/bin/bash

set -e

# Source variables, compilers, and modules:
################################################################################
source "./_export.cfg"

# Configuration/Parameters:
################################################################################
ARGS="--dim=2"
# PDE (fluid-dynamics|turbulence)
PDE="fluid-dynamics"
PRM_FILE="lid_cavity_2D.prm"
# PRM_FILE="flow_past_a_cylinder_2D_00.prm"
# viscosity:
nu=0.1
# number of refinemens:
ref=7
# stepper (euler|ida):
stepper=euler
# div-grad stabilization
div-grad=1.0

# Compute:
################################################################################

BASE_FOLDER="__simulations/${PDE}/prm=${PRM_FILE}/nu=${nu}/ref=${ref}/stepper=${stepper}/"

cd ${NESSUS_DIR}
NEXT_DIR=`${GET_NEXT_DIR} -F ${BASE_FOLDER} -f ${RUN_FOLDER}`
mkdir -p ${NEXT_DIR}
cd ${NEXT_DIR}

PRM_USED="parameters.prm"
cp "${NESSUS_DIR}/_utils/prm/${PDE}/${PRM_FILE}" ${PRM_USED}

${FIND_AND_REPLACE} "_NU_" ${nu} ${PRM_USED}
${FIND_AND_REPLACE} "_REF_" ${ref} ${PRM_USED}
${FIND_AND_REPLACE} "_STEPPER_" ${stepper} ${PRM_USED}
${FIND_AND_REPLACE} "_DIV-GRAD_" ${div-grad} ${PRM_USED}
${FIND_AND_REPLACE} "_UTILS_PATH_" "${NESSUS_DIR}/_utils" ${PRM_USED}

mpirun -np 3 ${EXECUTABLE_FOLDER}/${PDE} ${ARGS} \
  "--prm=${PRM_USED}" | tee ${OUTPUT_LOG_FILE}

CHECK=`ls *vtu 2>/dev/null`
if [[ ! -z ${CHECK} ]] 
then
  mkdir ${IMAGES_DIR}
  mv *vtu ${IMAGES_DIR} 
fi

touch "__JOB_COMPLETED__"
