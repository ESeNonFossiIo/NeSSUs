#!/usr/bin/env python

import ConfigParser
import os

def make_next_dir(  progress_dir="run", 
                    separation_char="_", 
                    base_directory="output/",
                    lenght=4):
  
  if not os.path.exists(base_directory):
    os.makedirs(base_directory)

  numbers=[]
  for name in os.listdir(base_directory):
    if (  os.path.isdir(os.path.join(base_directory, name)) and
          name.find(progress_dir)>=0 ) :
      numbers.append( int( str(name).replace(progress_dir + separation_char, '') ) )
  numbers.append(-1)
  maximum = str ( max(numbers) + 1 )
  zeroes =  "0" * ( lenght - len(maximum) )
  new_dir = base_directory + progress_dir + separation_char + zeroes + maximum
  os.makedirs(new_dir)
  
  return new_dir

from shutil import copyfile

# copyfile(src, dst)

config = ConfigParser.ConfigParser()
config.optionxform=str
config.read('./_conf/configuration.conf')

import itertools

simulation = ConfigParser.ConfigParser()
simulation.optionxform=str
simulation.read('./job_settings.conf')

print simulation.sections()



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
import pprint
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(simulations)

BASE_FOLDER="__simulations/${PDE}/${PRM_FILE}/${nu}/${ref}/${stepper}/"

prm_filename=config.get("OUTPUT","PRM_FILENAME")
base_name=config.get("OUTPUT", "BASE_FOLDER")
run_folder=config.get("OUTPUT","RUN_FOLDER")
images_dir=config.get("OUTPUT","IMAGES_DIR")
output_log_file=config.get("OUTPUT","OUTPUT_LOG_FILE")

NeSSUs_dir=config.get("PATHS","NESSUS_DIR")
NeSSUs_dir=NeSSUs_dir.replace('@PWD',os.getcwd())
utils_path=NeSSUs_dir+"/_utils/"

executable_folder=config.get("PATHS","EXECUTABLE_FOLDER")
executable_folder=executable_folder.replace('@PWD',os.getcwd())

# cp "${NESSUS_DIR}/_utils/prm/${PDE}/${PRM_FILE}" ${PRM_USED}

def get_value(dictionary, value):
  try:
    return_value=dictionary[value]
  except:
    return_value=""
  return return_value

num=0
for s in simulations:
  for run in simulations[s]:
    pde=get_value(run, "_PDE_")
    prm_file=get_value(run, "_PRM_")
    nu=get_value(run, "_NU_")
    ref=get_value(run, "_REF_")
    stepper=get_value(run, "_STEPPER_")
    
    folder="./"+base_name
    folder+="/"+pde
    folder+="/"+prm_file
    folder+="/"+nu
    folder+="/"+ref
    folder+="/"+stepper+"/"

    folder = make_next_dir( progress_dir="run", 
                            separation_char="_", 
                            base_directory=folder,
                            lenght=4)
                    
    old_prm_file=NeSSUs_dir
    old_prm_file+="/_utils/prm"
    old_prm_file+="/"+pde
    old_prm_file+="/"+prm_file

    new_prm_file=folder
    new_prm_file+="/"+prm_filename

    ext=get_value(run,"_TYPE_")
    
    job_file="_job_"
    job_file+=str(num)
    job_file+="_"+pde
    job_file+="_"+prm_file
    job_file+="."+ext

    num+=1
# with open('path/to/input/file') as infile, open('path/to/output/file', 'w') as outfile:
#     for line in infile:
#         for src, target in replacements.iteritems():
#             line = line.replace(src, target)
#         outfile.write(line)

# Write new prm file:
    with open(new_prm_file, "wt") as fout,\
         open(old_prm_file, "rt") as fin:
      for line in fin:
          for src, target in run.iteritems():
              line = line.replace(src, target)
          line = line.replace("_UTILS_PATH_",utils_path)
          fout.write(line)

# Write new job_file
    with open(job_file, "wt") as fout,\
         open("./_conf/_template."+ext, "rt") as fin:
      for line in fin:
        
          if get_value(run, "_PBS_NAME_") != "__NULL__" :
            pbs = "\n#PBS -N " + get_value(run, "_PBS_NAME_")
          else:
            pbs =  "\n#PBS -N " + prm_filename.replace(".prm", "")
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
          line = line.replace("_EXECUTABLE_FOLDER_", executable_folder)
          line = line.replace("_OUTPUT_LOG_FILE_", output_log_file)
          line = line.replace("_IMAGES_DIR_", images_dir)
          line = line.replace("_PBS_", pbs)
          line = line.replace("_PRMNAME_", prm_filename)
          line = line.replace("_SOURCE_MODULE_PATH_", images_dir)
          line = line.replace("_WORK_DIR_", NeSSUs_dir+"/launch_scripts/"+folder)
          fout.write(line)

    # print old_prm_file
    # print folder
    # print 
  # v=simulation.options(s)
  # for combination in combinations:
  #   file_name=s+str(num)
  # 
  #   
  #     fout.write("#!/bin/bash\n")
  #     if simulation.get(s,"_TYPE_") == "pbs":
  #       fout.write("#!/bin/bash\n")
  #     with open("./_template.pbs", "rt") as fin:
  #         for line in fin:
  #           new_line = line
  #           for i in combination:
  #               old, new = i.split("=")
  #               print new_line
  #               new_line=new_line.replace(old, new)
  #               print new_line
  #               print old + "---->" + new
  #           fout.write(new_line)
  #   fout.close()
  # 
  #   num+=1
    
    #   print var
    # 
    # name_job="_tmp_$
    # name_job+="_prm="+str(prm)
    # name_job+="_nu="+str(nu)
    # name_job+="_ref="+str(ref)
    # name_job+="_stepper="+str(stepper)
    # copyfile("_template.pbs", name_job)
    # 
    # ${FIND_AND_REPLACE} "__PDE__" ${PDE} ${NAME_JOB}
    # ${FIND_AND_REPLACE} "__DIM__" ${dim} ${NAME_JOB}
    # ${FIND_AND_REPLACE} "__PRM__" ${prm} ${NAME_JOB}
    # ${FIND_AND_REPLACE} "__NU__" ${nu} ${NAME_JOB}
    # ${FIND_AND_REPLACE} "__REF__" ${ref} ${NAME_JOB}
    # ${FIND_AND_REPLACE} "__STEPPER__" ${stepper} ${NAME_JOB}
    # ${FIND_AND_REPLACE} "__DIV_GRAD__" ${div_grad} ${NAME_JOB}
# f1 = open('yourBigFile.txt', 'r')
# f2 = open('yourBigFile.txt.tmp', 'w')
# for line in f1:
#     f2.write(line.replace(';', ' '))
# f1.close()
# f2.close()
