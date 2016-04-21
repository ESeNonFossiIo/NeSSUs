#!/usr/bin/env python

"""
  MaJOrCA - Multiple JObs CreAtor
"""

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
import PUlSe_directories as pdir
import PUlSe_string as pstring

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

out.assert_msg( os.path.isfile(options.configuration_file), 
            str(options.configuration_file), "existence" )

out.var("Conf file", options.configuration_file)
config = ConfigParser.ConfigParser()
config.optionxform=str #case sensitive
config.read(options.configuration_file)

sections = config.sections()
# Get data from GENERAL section:
general_val = utils.GetValFromConfParser(out, config, "GENERAL")
general = dict()

pstring.fill_dictionary_with_config_parser( dictionary = general, 
                                            confparser = config, 
                                            section = "GENERAL" )

out.print_dictionary(dictionary=general)

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
    values_entries = []
    ee = utils.EvalExpression(config.get(s, v))
    for opt in ee().split(general['SEP']):
      values_entries.append([v, PE.process(opt)])
    values.append(values_entries)

  # Evaluate all possibile combiation between values and store this result
  # as a dictionary:
  combinations = list(itertools.product(*values))
  
  for c in combinations:
    for item in c:
      if item[1] == '' :
        item[1]=null_token
    simulation.append(dict(c))
    local_vars.append(copy.deepcopy(general))

  PE.process_a_simulation(local_vars)
  simulations[s] = simulation
  local_var[s] = local_vars

out.close_section()

# Create folders and jobs:
for s in simulations:
  out.title("SIMULATION "+str(s))
  for n in xrange(len(simulations[s])):
    job = local_var[s][n]
    
    out.close_subsection()
    dictionary_val = utils.GetValFromDictionary(out, simulations[s][n])
    job["EXECUTABLE"] = dictionary_val.get("EXECUTABLE",    output=True)
    job["ARGS"] = dictionary_val.get("ARGS",    output=True)
    bp_prm     = dictionary_val.get("BLUEPRINT_PRM", output=True)
    mode       = dictionary_val.get("MODE",          output=True)

    # fix mode:
    if mode == "sh":
      job["PBS"] = ""
    elif mode == "pbs":
      job["PBS"] = "\n#PBS -N "
      if dictionary_val.get("PBS_NAME") != null_token :
        job["PBS"] += dictionary_val.get("PBS_NAME")
      else:
        job["PBS"] += job['PRM_FILENAME'].replace(".prm", "")
      if dictionary_val.get("PBS_WALLTIME") != null_token :
        job["PBS"] += "\n#PBS -l walltime=" + dictionary_val.get("PBS_WALLTIME")
      if dictionary_val.get("PBS_NODES") != null_token :
        job["PBS"] += "\n#PBS -l " + dictionary_val.get("PBS_NODES")
      if dictionary_val.get("PBS_QUEUE") != null_token :
        job["PBS"] += "\n#PBS -q " + dictionary_val.get("PBS_QUEUE") 
      if dictionary_val.get("PBS_MAIL") != null_token :
        job["PBS"] += "\n#PBS -M " + dictionary_val.get("PBS_MAIL")
        job["PBS"] +=  "\n#PBS -m abe"
      job["PBS"] +="\n"
    else:
      break    

    # create prm folder:
    job['FOLDER']=job['BASE_FOLDER']
    for src, target in simulations[s][n].iteritems():
        job['FOLDER'] = job['FOLDER'].replace(job['PTOKEN']+str(src)+job['PTOKEN'], target)

    job['FOLDER'] = pdir.make_next_dir( progress_dir=job['RUN_FOLDER'], 
                            separation_char=job['RUN_FOLDER-SEP_CHAR'], 
                            base_directory=job['FOLDER'],
                            lenght=int(job['RUN_FOLDER-LEN']))

    prm=os.path.normpath(job['FOLDER']+"/"+job['PRM_FILENAME'])
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
        job['JOBS_FOLDER_NAME'] = job['JOBS_FOLDER_NAME'].replace(job['PTOKEN']+str(src)+job['PTOKEN'], target) 
    if not os.path.exists(job['JOBS_FOLDER_NAME']):
      os.makedirs(job['JOBS_FOLDER_NAME'])

    job['JOBS_NAME']=pdir.get_next( 
                                  job['JOBS_NAME'], 
                                  mode, job['JOBS_FOLDER_NAME'], 
                                  job['JOBS_NAME-SEP_CHAR'],
                                  int(job['JOBS_NAME-LEN']))
    job['JOBS_NAME']+="."+mode
    out.var("JOB FILE", job['JOBS_FOLDER_NAME']+job['JOBS_NAME'])

    job['WORK_DIR'] = job['FOLDER']
    
    # Write job file:
    with open(job['JOBS_FOLDER_NAME']+job['JOBS_NAME'], "wt") as fout:
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
            target = job[src]
            line = rh.replace(line, src, target)
            if target.strip() == "" :
              line  = line.replace( job['PTOKEN']+src+job['PTOKEN'], "" )
              not_found_variables.append(src)
          for key, val in job.iteritems():
            line = line.replace("@"+str(key)+"@", str(val))
          fout.write(line)
        for var in list(set(not_found_variables)):
          out.exception_msg(utils.Error.not_found, job['PTOKEN']+var+job['PTOKEN'])
  out.close_subsection()

out.close_section()
