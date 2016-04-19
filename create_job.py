#!/usr/bin/env python

from optparse import OptionParser
from shutil import copyfile
import os
import sys
import itertools
import ConfigParser
import _lib.utils as utils
import copy

# Add path to PUlSe and this module:
pulse_dir="./_modules/PUlSe/lib/"
sys.path.append(pulse_dir)
from PUlSe_directories import *

# Parse CLI parameters:
################################################################################ 
parser = OptionParser()

parser.add_option("-f", "--file", 
                  dest="configuration_file",
                  default="./_template/template.conf",
                  help="`conf` file. (See _template/template.conf).", 
                  metavar="FILE")

parser.add_option("-c", "--conf",
                  dest="new_configuration_file",
                  default="",
                  help="generate ./filename.conf copying _template/template.conf.", 
                  metavar="FILE")

(options, args) = parser.parse_args()

# Preliminary operations:
################################################################################ 

out = utils.Output(100)
out.title("Configuration ")

if options.new_configuration_file != "":
  out.assert_msg( os.path.isfile("_template/template.conf"), 
              "_template/template.conf", "existence" )
  copyfile(  "_template/template.conf",
              options.new_configuration_file)
  out.close_section()
  sys.exit(1)
  
# Main:
################################################################################ 
PE = utils.ProcessEntry(out)
out.assert_msg( os.path.isfile(options.configuration_file), 
            str(options.configuration_file), "existence" )

out.var("Conf file", options.configuration_file)
config = ConfigParser.ConfigParser()
config.optionxform=str #case sensitive
config.read(options.configuration_file)

sections = config.sections()
# Get data from GENERAL section:
general_val = utils.GetValFromConfParser(out, config, "GENERAL")
general=dict()

for key in config.items("GENERAL"):
  general[key[0]] = general_val.get(key[0], output=True)

# Run folder vars
general['RUN_FOLDER-LEN']       = general['RUN_FOLDER'].count('$')
general['RUN_FOLDER']           = general['RUN_FOLDER'].replace('$', '')
general['RUN_FOLDER-SEP_CHAR']  = general['RUN_FOLDER'][-1]
general['RUN_FOLDER']           = general['RUN_FOLDER'][0:-1]
out.var("RUN_FOLDER", general['RUN_FOLDER'])
out.var("SEP CHAR", general['RUN_FOLDER-SEP_CHAR'])
out.var("NUM ZEROS", general['RUN_FOLDER-LEN'])

# Jobs name vars:
general['JOBS_NAME-LEN']      = general['JOBS_NAME'].count('$')
general['JOBS_NAME']          = general['JOBS_NAME'].replace('$', '')
general['JOBS_NAME-SEP_CHAR'] = general['JOBS_NAME'][-1]
general['JOBS_NAME']          = general['JOBS_NAME'][0:-1]
out.var("JOBS NAME",     general['JOBS_NAME'])
out.var("SEP CHAR JOBS", general['JOBS_NAME-SEP_CHAR'])
out.var("JOB NUM ZEROS", general['JOBS_NAME-LEN'])

sections.remove('GENERAL')

# placeholder for NULL entries
null_token = general['PTOKEN']+"NULL"+general['PTOKEN']
# Define ReplaceHelper (see: lib/utils.py)
rh = utils.ReplaceHelper(general['PTOKEN'])

# Fill the dictionary simulations with all possibile combination of every 
# parameter of every single simulation:
simulations=dict()
local_var=dict()
for s in sections:
  simulation=[]
  values=[]
  local_vars=[]
  
  PE = utils.ProcessEntry(out, section=s)
  # Get all value of this simulation: 
  for v in config.options(s):
    values.append( [ [v, PE.process(opt)]  for opt in config.get(s, v).split(general['SEP'])] )

  # Evaluate all possibile combiation between values and store this result
  # as a dictionary:
  combinations = list(itertools.product(*values))
  
  for c in combinations:
    for item in c:
      if item[1] == '' :
        item[1]=null_token
    simulation.append(dict(c))
    local_vars.append(copy.deepcopy(general))
  simulations[s] = simulation
  local_var[s] = local_vars

out.close_section()

# Create folders and jobs:
for s in simulations:
  out.title("SIMULATION "+str(s))
  for n in xrange(len(simulations[s])):
    out.close_subsection()
    dictionary_val = utils.GetValFromDictionary(out, simulations[s][n])
    local_var[s][n]["EXECUTABLE"] = dictionary_val.get("EXECUTABLE",    output=True)
    local_var[s][n]["ARGS"] = dictionary_val.get("ARGS",    output=True)
    bp_prm     = dictionary_val.get("BLUEPRINT_PRM", output=True)
    mode       = dictionary_val.get("MODE",          output=True)

    # fix mode:
    if mode == "sh":
      local_var[s][n]["PBS"] = ""
    elif mode == "pbs":
      local_var[s][n]["PBS"] = "\n#PBS -N "
      if dictionary_val.get("PBS_NAME") != null_token :
        local_var[s][n]["PBS"] += dictionary_val.get("PBS_NAME")
      else:
        local_var[s][n]["PBS"] += local_var[s][n]['PRM_FILENAME'].replace(".prm", "")
      if dictionary_val.get("PBS_WALLTIME") != null_token :
        local_var[s][n]["PBS"] += "\n#PBS -l walltime=" + dictionary_val.get("PBS_WALLTIME")
      if dictionary_val.get("PBS_NODES") != null_token :
        local_var[s][n]["PBS"] += "\n#PBS -l " + dictionary_val.get("PBS_NODES")
      if dictionary_val.get("PBS_QUEUE") != null_token :
        local_var[s][n]["PBS"] += "\n#PBS -q " + dictionary_val.get("PBS_QUEUE") 
      if dictionary_val.get("PBS_MAIL") != null_token :
        local_var[s][n]["PBS"] += "\n#PBS -M " + dictionary_val.get("PBS_MAIL")
        local_var[s][n]["PBS"] +=  "\n#PBS -m abe"
      local_var[s][n]["PBS"] +="\n"
    else:
      break    

    # create prm folder:
    local_var[s][n]['FOLDER']=general['BASE_FOLDER']
    for src, target in simulations[s][n].iteritems():
        local_var[s][n]['FOLDER'] = local_var[s][n]['FOLDER'].replace(local_var[s][n]['PTOKEN']+str(src)+local_var[s][n]['PTOKEN'], target)

    local_var[s][n]['FOLDER'] = make_next_dir( progress_dir=local_var[s][n]['RUN_FOLDER'], 
                            separation_char=general['RUN_FOLDER-SEP_CHAR'], 
                            base_directory=local_var[s][n]['FOLDER'],
                            lenght=general['RUN_FOLDER-LEN'])

    prm=os.path.normpath(local_var[s][n]['FOLDER']+"/"+local_var[s][n]['PRM_FILENAME'])
    out.var("PRM FILE", prm)

    # Write new prm file:
    with open(prm, "wt") as fout:
      with open(bp_prm, "rt") as fin:
        for line in fin:
            for src, target in simulations[s][n].iteritems():
              if target != null_token :
                line = rh.replace(line, src, target)             
              else:
                line = rh.replace_with_default_value(line, src)  
            fout.write(line)

    # create job foldes:
    for src, target in simulations[s][n].iteritems():
        local_var[s][n]['JOBS_FOLDER_NAME'] = local_var[s][n]['JOBS_FOLDER_NAME'].replace(local_var[s][n]['PTOKEN']+str(src)+local_var[s][n]['PTOKEN'], target) 
    if not os.path.exists(local_var[s][n]['JOBS_FOLDER_NAME']):
      os.makedirs(local_var[s][n]['JOBS_FOLDER_NAME'])

    local_var[s][n]['JOBS_NAME']=get_next( 
                                  local_var[s][n]['JOBS_NAME'], 
                                  mode, local_var[s][n]['JOBS_FOLDER_NAME'], 
                                  general['JOBS_NAME-SEP_CHAR'],
                                  general['JOBS_NAME-LEN'])
    local_var[s][n]['JOBS_NAME']+="."+mode
    out.var("JOB FILE", local_var[s][n]['JOBS_FOLDER_NAME']+local_var[s][n]['JOBS_NAME'])

    local_var[s][n]['WORK_DIR'] = local_var[s][n]['FOLDER']
    
    # Write job file:
    with open(local_var[s][n]['JOBS_FOLDER_NAME']+local_var[s][n]['JOBS_NAME'], "wt") as fout:
      with open("./_template/template.sh", "rt") as fin:
        not_found_variables = []
        for line in fin:  
          for src, target in simulations[s][n].iteritems():
            if target != null_token :  
              line = rh.replace(line, src, target)
            else:
              line = rh.replace_with_default_value(line, src) 
          for src in [  "FOLDER", 
                        "WORK_DIR",
                        "OUTPUT_LOG_FILE", 
                        "ERROR_LOG_FILE",
                        "PREPROCESS",
                        "POSTPROCESS",
                        "PBS",
                        "EXECUTABLE"]:
            target = local_var[s][n][src]
            line = rh.replace(line, src, target)
            if target.strip() == "" :
              line  = line.replace( local_var[s][n]['PTOKEN']+src+local_var[s][n]['PTOKEN'], "" )
              not_found_variables.append(src)
          for key, val in local_var[s][n].iteritems():
            line = line.replace("@"+str(key)+"@", str(val))
          fout.write(line)
        for var in list(set(not_found_variables)):
          out.exception_msg(utils.Error.not_found, local_var[s][n]['PTOKEN']+var+local_var[s][n]['PTOKEN'])
  out.close_subsection()

out.close_section()
