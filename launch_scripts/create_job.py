#!/usr/bin/env python


import ConfigParser
import os
import sys
from shutil import copyfile
import itertools

config = ConfigParser.ConfigParser()
config.optionxform=str
config.read('./_conf/configuration.conf')

NeSSUs_dir=config.get("PATHS","NESSUS_DIR")
NeSSUs_dir=NeSSUs_dir.replace('@PWD',os.getcwd())

# Add path tu PUlSe:
PUlSe_dir=NeSSUs_dir+"/_modules/PUlSe/lib/"
sys.path.append(PUlSe_dir)

# print sys.path
from PUlSe_directories import *

simulation = ConfigParser.ConfigParser()
simulation.optionxform=str
simulation.read('./job_settings.conf')

# print simulation.sections()



simulations=dict()
for s in simulation.sections():
  val=[]
  values=[]
  num=0

  for v in simulation.options(s):
    values.append( [ [v, opt]  for opt in simulation.get(s, v).split(" ")] )

  combinations = list(itertools.product(*values))
  for c in combinations:
    for item in c:
      if item[1] == '' :
        item[1]="__NULL__"
    val.append(dict(c))
  simulations[s] = val
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(simulations)

# BASE_FOLDER="__simulations/${PDE}/${PRM_FILE}/${nu}/${ref}/${stepper}/"

prmname=config.get("OUTPUT","PRM_FILENAME")
base_name=config.get("OUTPUT", "BASE_FOLDER")
run_folder=config.get("OUTPUT","RUN_FOLDER")
images_dir=config.get("OUTPUT","IMAGES_DIR")
output_log_file=config.get("OUTPUT","OUTPUT_LOG_FILE")
jobs_folder_name=config.get("OUTPUT","JOBS_FOLDER_NAME")

utils_path=NeSSUs_dir+"/_utils/"

executable_folder=config.get("PATHS","EXECUTABLE_FOLDER")
executable_folder=executable_folder.replace('@PWD',os.getcwd())
source_module_path=config.get("PATHS", "SOURCE_MODULE_PATH")

def get_value(dictionary, value):
  try:
    return_value=dictionary[value]
  except:
    return_value=""
  return return_value

def get_var_name(**arg):
  return arg.keys()[0]

num=0
for s in simulations:
  print "\n\n SIMULATION: " + str(s)
  for run in simulations[s]:
    pde=get_value(run, "_PDE_")
    dim=get_value(run, "_DIM_")
    prm_file=get_value(run, "_PRM_")
    nu=get_value(run, "_NU_")
    ref=get_value(run, "_REF_")
    stepper=get_value(run, "_STEPPER_")
    
    folder="./"+ str(base_name)
    folder+="/"+ str(s) 
    folder+="/"+ pde
    folder+="/"+ prm_file
    # folder+="/"
    # folder+="/"+nu
    # folder+="/"+ref
    # folder+="/"+stepper+"/"

    folder = make_next_dir( progress_dir="run", 
                            separation_char="_", 
                            base_directory=folder,
                            lenght=4)
    
    work_dir=NeSSUs_dir+"/launch_scripts/"+folder
                    
    old_prm_file=NeSSUs_dir
    old_prm_file+="/_utils/prm"
    old_prm_file+="/"+pde
    old_prm_file+="/"+dim+"D"
    old_prm_file+="/"+prm_file

    new_prm_file=folder
    new_prm_file+="/"+prmname

    ext=get_value(run,"_TYPE_")

    if not os.path.exists("./"+jobs_folder_name+"/"):
      os.makedirs("./"+jobs_folder_name+"/")
    
    job_file="./"+jobs_folder_name+"/_job_"
    job_file+=str(num)
    job_file+="_"+s+"_"
    job_file+="_"+pde
    job_file+="_"+prm_file.replace(".prm", "")
    job_file+="."+ext

    print " \tJob:  \t -> "+str(job_file)
    num+=1
    
# Write new prm file:
    with open(new_prm_file, "wt") as fout:
      with open(old_prm_file, "rt") as fin:
        for line in fin:
            for src, target in run.iteritems():
                line = line.replace(src, target)
            line = line.replace("_UTILS_PATH_",utils_path)
            fout.write(line)

# Write new job_file
    with open(job_file, "wt") as fout:
      with open("./_conf/_template."+ext, "rt") as fin:
        for line in fin:

            pbs = "\n#PBS -N job_" + str(num) + " "
            if get_value(run, "_PBS_NAME_") != "__NULL__" :
              pbs += get_value(run, "_PBS_NAME_")
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
            
            for src, target in run.iteritems():
              if target != "__NULL__" :
                line = line.replace(src, target)
              else:
                line = line.replace(src, " ")
            for src in [ "_EXECUTABLE_FOLDER_", "_WORK_DIR_", "_OUTPUT_LOG_FILE_", "_IMAGES_DIR_", "_PBS_", "_PRMNAME_", "_SOURCE_MODULE_PATH_"]:
              target = eval(src[1:-1].lower())
              line = line.replace(src, target)
            fout.write(line)

