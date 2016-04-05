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
  new_dir = base_directory + progress_dir + separation_char + num
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
simulation.read('./simulations.conf')

values=[]
for simulations in simulation.sections():
  for variables in simulation.options(simulations):
    values.append(simulation.get(simulations, variables).split(" "))
  combinations = list(itertools.product(*values))

  variables=simulation.options(simulations)
  for combination in combinations:
    print "========================="
    for i in xrange(len(combination)):
      print variables[i]
      print combination[i]
      print "-------------------------"

    
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
