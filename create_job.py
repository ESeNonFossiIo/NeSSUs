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

out = Output(50)
out.title("Configuration ")

if options.new_configuration_file != "":
  out.ASSERT( os.path.isfile("_template/template.conf"), 
              "_template/template.conf", "existence" )
  copyfile(  "_template/template.conf",
              options.new_configuration_file)
  out.close_section()
  sys.exit(1)
  
# Main:
################################################################################ 
PE = ProcessEntry(out)
out.ASSERT( os.path.isfile(options.configuration_file), 
            str(options.configuration_file), "existence" )

out.var("Conf file", options.configuration_file)
config = ConfigParser.ConfigParser()
config.optionxform=str #case sensitive
config.read(options.configuration_file)

sections = config.sections()
# Get data from GENERAL section:
general_val = GetValFromConfParser(out, config, "GENERAL")
sep_char          = general_val.get("SEP", output=True)
base_name         = general_val.get("BASE_FOLDER", output=True)
output_log_file   = general_val.get("OUTPUT_LOG_FILE", output=True)
error_log_file    = general_val.get("ERROR_LOG_FILE", output=True)
jobs_folder_name  = general_val.get("JOBS_FOLDER_NAME", output=True)
run_folder        = general_val.get("RUN_FOLDER", output=False)
num_zeros         = run_folder.count('$')
run_folder        = run_folder.replace('$', '')
spc               = run_folder[-1]
run_folder        = run_folder[0:-1]
out.var("RUN_FOLDER", run_folder)
out.var("SEP CHAR", spc)
out.var("NUM ZEROS", num_zeros)
jobs_name         = general_val.get("JOBS_NAME", output=False)
jobs_num_zeros    = jobs_name.count('$')
jobs_name         = jobs_name.replace('$', '')
jobs_spc          = jobs_name[-1]
jobs_name         = jobs_name[0:-1]
out.var("JOBS NAME", jobs_name)
out.var("SEP CHAR JOBS", jobs_spc)
out.var("JOB NUM ZEROS", jobs_num_zeros)
jobs_folder_name
prm_filename      = general_val.get("PRM_FILENAME", output=True)

sections.remove('GENERAL')

# Fill the dictionary simulations with all possibile combination of every 
# parameter of every single simulation:
simulations=dict()
for s in sections:
  simulation=[]
  values=[]

  PE = ProcessEntry(out, section=s)
  # Get all value of this simulation: 
  for v in config.options(s):
    values.append( [ [v, PE.process(opt)]  for opt in config.get(s, v).split(sep_char)] )

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
      pbs = "\n#PBS -N "
      if dictionary_val.get("PBS_NAME") != "__NULL__" :
        pbs += dictionary_val.get("PBS_NAME")
      else:
        pbs += dictionary_val.get("PRM").replace(".prm", "")
      if dictionary_val.get("PBS_WALLTIME") != "__NULL__" :
        pbs += "\n#PBS -l walltime=" + dictionary_val.get("PBS_WALLTIME")
      if dictionary_val.get("PBS_NODES") != "__NULL__" :
        pbs += "\n#PBS -l " + dictionary_val.get("PBS_NODES")
      if dictionary_val.get("PBS_QUEUE") != "__NULL__" :
        pbs += "\n#PBS -q " + dictionary_val.get("PBS_QUEUE") 
      if dictionary_val.get("PBS_MAIL") != "__NULL__" :
        pbs += "\n#PBS -M " + dictionary_val.get("PBS_MAIL")
        pbs +=  "\n#PBS -m abe"
      pbs+="\n"
    else:
      break    

    # create prm folder:
    folder=base_name
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
              if target != "__NULL__" :
                line = line.replace("__"+src+"__", target)
              else:
                size  = 6 + len(src)
                start = line.find("__"+src+"__[[")+size
                end   = line.find("]]", start)
                val   = line[start:end]
                line  = line.replace("__"+src+"__[["+val+"]]", val)
            fout.write(line)

    # create job foldes:
    job_file=jobs_folder_name
    for src, target in simulation.iteritems():
        job_file = job_file.replace("__"+str(src)+"__", target) 
    if not os.path.exists(job_file):
      os.makedirs(job_file)
          
    job_file+=get_next(jobs_name,mode,job_file,jobs_spc,jobs_num_zeros)
    job_file+="."+mode
    out.var("JOB FILE", job_file + "")
    
    # Job vars:
    work_dir=folder
    # mpirun_flags=" "
    args_exec=""
    
    # Write job file:
    with open(job_file, "wt") as fout:
      with open("./_template/template.sh", "rt") as fin:
        for line in fin:  
          for src, target in simulation.iteritems():
            if target != "__NULL__" :
              line = line.replace("__"+src+"__", target)
            else:
              size  = 6 + len(src)
              start = line.find("__"+src+"__[[")+size
              end   = line.find("]]", start)
              val   = line[start:end]
              line  = line.replace("__"+src+"__[["+val+"]]", val)
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