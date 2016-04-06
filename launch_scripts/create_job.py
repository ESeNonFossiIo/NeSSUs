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

base_name=config.get("OUTPUT", "BASE_FOLDER")
prm_filename=config.get("OUTPUT","PRM_FILENAME")

NeSSUs_dir=config.get("PATHS","NESSUS_DIR")
NeSSUs_dir=NeSSUs_dir.replace('@PWD',os.getcwd())

# cp "${NESSUS_DIR}/_utils/prm/${PDE}/${PRM_FILE}" ${PRM_USED}

def get_value(dictionary, value):
  try:
    return_value=dictionary[value]
  except:
    return_value=""
  return return_value

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

# with open('path/to/input/file') as infile, open('path/to/output/file', 'w') as outfile:
#     for line in infile:
#         for src, target in replacements.iteritems():
#             line = line.replace(src, target)
#         outfile.write(line)
        
    with open(new_prm_file, "wt") as fout,\
         open(old_prm_file, "rt") as fin:
      for line in fin:
          for src, target in run.iteritems():
              line = line.replace(src, target)
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
