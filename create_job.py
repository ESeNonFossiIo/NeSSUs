#!/usr/bin/env python

from optparse import OptionParser
from shutil import copyfile
import sys
import itertools
import ConfigParser
from _lib.utils import *

# import os

# Add path to PUlSe and this module:
PUlSe_dir="./_modules/PUlSe/lib/"
sys.path.append(PUlSe_dir)
from PUlSe_directories import *

# Parse CLI parameters:
################################################################################ 
parser = OptionParser()

parser.add_option("-f", "--file", 
                  dest="configuration_file",
                  default="./job.conf",
                  help="`conf` file. (See _template/template_conf.template).", 
                  metavar="FILE")

parser.add_option("-c", "--conf",
                  dest="new_configuration_file",
                  default="",
                  help="generate ./filename.conf copying _template/template_conf.template.", 
                  metavar="FILE")

(options, args) = parser.parse_args()

# Preliminary operations:
################################################################################ 

if options.new_configuration_file != "":
  # TODO: add a check on the existence of the file.
  copyfile(  "_template/template_conf.template",
              options.new_configuration_file)
  sys.exit(1)
  
# Main:
################################################################################ 

out = Output(50)
out.title("Configuration ")
PE = ProcessEntry(out)

# TODO: add a check on the existence of the file.
# if option.configuration_file does not exists..

out.var("Conf file", options.configuration_file)
config = ConfigParser.ConfigParser()
config.optionxform=str #case sensitive
config.read(options.configuration_file)

sections = config.sections()
sections.remove('GENERAL')

# Get data from GENERAL section:
general_val = GetValFromConfParser(out, config, "GENERAL")

base_name         = general_val.get("BASE_FOLDER", output=True)
run_folder        = general_val.get("RUN_FOLDER", output=False)
num_zeros         = run_folder.count('$')
run_folder        = run_folder.replace('$', '')
spc               = run_folder[-1]
run_folder        = run_folder[0:-1]
out.var("RUN_FOLDER", run_folder)
out.var("SEP CHAR", spc)
out.var("NUM ZEROS", num_zeros)
output_log_file   = general_val.get("OUTPUT_LOG_FILE", output=True)
error_log_file    = general_val.get("ERROR_LOG_FILE", output=True)
jobs_folder_name  = general_val.get("JOBS_FOLDER_NAME", output=True)
prm_filename      = general_val.get("PRM_FILENAME", output=True)

# Fill the dictionary simulations with all possibile combination of every 
# parameter of every single simulation:
simulations=dict()
for s in sections:
  simulation=[]
  values=[]
  
  # Get all value of this simulation: 
  for v in config.options(s):
    values.append( [ [v, opt]  for opt in config.get(s, v).split(";")] )

  # Evaluate all possibile combiation between values and store this result
  # as a dictionary:
  combinations = list(itertools.product(*values))
  for c in combinations:
    for item in c:
      if item[1] == '' :
        item[1]="__NULL__"
    simulation.append(dict(c))
  simulations[s] = simulation

out.close_section()

# Create folders and jobs:
for s in simulations:
  out.title("SIMULATION "+str(s))
  for simulation in simulations[s]:
    out.close_subsection()
    dictionary_val = GetValFromDictionary(out, simulation)
    executable = dictionary_val.get("EXECUTABLE",    output=True)
    bp_prm     = dictionary_val.get("BLUEPRINT_PRM", output=True)
    mode       = dictionary_val.get("MODE",          output=True)

    # fix mode:
    if mode == "sh":
      pbs = ""
    elif mode == "pbs":
      pbs = "\n#PBS -N job_" + str(num) + " "
      if get_value(run, "_PBS_NAME_") != "__NULL__" :
        pbs += get_value(run, "_PBS_NAME_") # TODO: check this!
      else:
        pbs += get_value(run, "_PRM_").replace(".prm", "")
      if get_value(run, "_PBS_WALLTIME_") != "__NULL__" :
        pbs += "\n#PBS -l walltime=" + get_value(run, "_PBS_WALLTIME_")
      if get_value(run, "_PBS_NODES_") != "__NULL__" :
        pbs += "\n#PBS -l " + get_value(run, "_PBS_NODES_")
      if get_value(run, "_PBS_QUEUE_") != "__NULL__" :
        pbs += "\n#PBS -q " + get_value(run, "_PBS_QUEUE_") 
      if get_value(run, "_PBS_MAIL_") != "__NULL__" :
        pbs += "\n#PBS -M " + get_value(run, "_PBS_MAIL_")
        pbs +=  "\n#PBS -m abe"
      pbs+="\n"
    else:
      break    

    # create prm folder:
    folder=base_name # TODO: improve using prm file...
    for src, target in simulation.iteritems():
        folder = folder.replace("__"+str(src)+"__", target)
    if not os.path.exists(base_name):
          os.makedirs(base_name)

    folder = make_next_dir( progress_dir=run_folder, 
                            separation_char=spc, 
                            base_directory=folder,
                            lenght=num_zeros)

    prm=folder+"/"+prm_filename
    out.var("PRM FILE", prm)

    # Write new prm file:
    with open(prm, "wt") as fout:
      with open(bp_prm, "rt") as fin:
        for line in fin:
            for src, target in simulation.iteritems():
                line = line.replace("__"+str(src)+"__", target)
            fout.write(line)

    # create job foldes:
    job_file=jobs_folder_name
    for src, target in simulation.iteritems():
        job_file = job_file.replace("__"+str(src)+"__", target)
    if not os.path.exists(job_file):
      os.makedirs(job_file)
    job_file+=get_next("job",mode,job_file,"_",3)
    job_file+="."+mode
    out.var("JOB FILE", job_file + "")
    
    # Job vars:
    work_dir=folder
    # mpirun_flags=" "
    args_exec=""
    
    # Write job file:
    with open(job_file, "wt") as fout:
      with open("./_template/template_job.template", "rt") as fin:
        for line in fin:  
          for src, target in simulation.iteritems():
            if target != "__NULL__" :
              line = line.replace("__"+src+"__", target)
            else:
              line = line.replace("__"+src+"__", " ")
          for src in [  "WORK_DIR", 
                        "OUTPUT_LOG_FILE", 
                        "ERROR_LOG_FILE",
                        "PBS",
                        "EXECUTABLE",
                        "ARGS_EXEC"]:
            target = eval(src.lower())
            line = line.replace("__"+src+"__", target)
          fout.write(line)
  out.close_subsection()

out.close_section()