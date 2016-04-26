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
import _lib.main as main
import copy

# Add path to PUlSe and this module:
pulse_dir="./_modules/PUlSe/lib/"
sys.path.append(pulse_dir)
import PUlSe_directories as pdir

# Parse CLI parameters:
################################################################################ 
parser = OptionParser()

parser.add_option("-f", "--file", 
                  dest="configuration_file",
                  default="./_conf/template.conf",
                  help="`conf` file. (See _conf/template.conf).", 
                  metavar="FILE")

parser.add_option("-c", "--conf",
                  dest="new_configuration_file",
                  default="",
                  help="generate ./filename.conf copying _conf/template.conf.", 
                  metavar="FILE")

parser.add_option("-j", "--jobs_file",
                  action='store_true',
                  default=False,
                  dest="jobs_file",
                  help="generate launch.sh.")
                  
(options, args) = parser.parse_args()

# Preliminary operations:
################################################################################ 

out = utils.Output(100)
out.title("Configuration ")

status = main.generate_new_conf_file( 
            new_file = options.new_configuration_file,
            old_file = "_conf/template.conf",
            output = out )
if status:
  sys.exit(1)
  
# Main:
################################################################################ 

out.assert_msg( os.path.isfile(options.configuration_file), 
            str(options.configuration_file), "existence" )

out.var("Conf file", options.configuration_file)

config = main.CP(options.configuration_file)
system = main.CP("_conf/system.conf")

general = dict()
config.fill( dictionary = general, section = "GENERAL" )

out.print_dictionary(dictionary=general)

config.remove_section('GENERAL')

for section_to_remove in general["SECTIONS_DISABLED"].split(general["SEP"]):
  config.remove_section(section_to_remove.strip())

# placeholder for NULL entries
general["NULL_TOKES"] = general['PTOKEN']+"NULL"+general['PTOKEN']

# Define ReplaceHelper (see: lib/utils.py)
rh = utils.ReplaceHelper(general['PTOKEN'])


# Fill the dictionary simulations with all possibile combination of every 
# parameter of every single simulation:
local_var=dict()
for s in config.get_sections():

  values=[]
  local_vars=[]

  PE = utils.ProcessEntry(out, section=s)
  # Get all value of this simulation: 
  for v in config.get_options(s):
    values_entries = []
    ee = utils.EvalExpression(config[s][v])
    for opt in ee().split(general['SEP']):
      values_entries.append([v, PE.process(opt)])
    values.append(values_entries)

  # Evaluate all possibile combiation between values and store this result
  # as a dictionary:
  combinations = list(itertools.product(*values))
  
  for c in combinations:
    for item in c:
      if item[1] == '' :
        item[1]=general["NULL_TOKES"]

    tmp_dict = copy.deepcopy(general)
    tmp_dict.update(dict(c))
    local_vars.append(copy.deepcopy(tmp_dict))

  PE.process_a_simulation(local_vars)
  local_var[s] = local_vars

out.close_section()

# Create folders and jobs:
for s in local_var:
  out.title("SIMULATION "+str(s))
  for simulation in local_var[s]:
    job = simulation
    
    out.close_subsection()
    
    main.sh_pbs_mode(job)

    # create prm folder:
    main.replace_entry_using_dictionary(job, "BASE_FOLDER")

    job['BASE_FOLDER'] = pdir.make_next_dir( progress_dir=job['RUN_FOLDER'], 
                            separation_char=job['RUN_FOLDER-SEP_CHAR'],
                            base_directory=job['BASE_FOLDER'],
                            lenght=int(job['RUN_FOLDER-LEN']))
    
    # PRM FILE:
    prm=os.path.normpath(job['BASE_FOLDER']+"/"+job['PRM_FILENAME'])
    out.var("PRM FILE", prm)
    
    # Write new prm file:
    with open(prm, "wt") as fout:
      with open(job["BLUEPRINT_PRM"], "rt") as fin:
        for line in fin:
          line = main.replace_line_using_dictionary(job, line, rh)
          fout.write(line)

    # create job foldes:
    main.replace_entry_using_dictionary(job, "JOBS_FOLDER_NAME")
            
    if not os.path.exists(job['JOBS_FOLDER_NAME']):
      os.makedirs(job['JOBS_FOLDER_NAME'])

    job['JOBS_NAME']=pdir.get_next( 
                                  job['JOBS_NAME'], 
                                  job["MODE"], job['JOBS_FOLDER_NAME'], 
                                  job['JOBS_NAME-SEP_CHAR'],
                                  int(job['JOBS_NAME-LEN']))
    job['JOBS_NAME']+="."+job["MODE"]
    
    out.var("JOB FILE", job['JOBS_FOLDER_NAME']+"/"+job['JOBS_NAME'])

    job['WORK_DIR'] = job['BASE_FOLDER']
    
    # Write job file:
    with open(job['JOBS_FOLDER_NAME']+"/"+job['JOBS_NAME'], "wt") as fout:
      with open("./_conf/template.sh", "rt") as fin:
        # not_found_variables = []
        for line in fin:  
          for src, target in job.iteritems():
            line = main.replace_line_using_dictionary(job, line, rh)
          for src in system["script"]["DIRS"].split(" "):
            target = job[src]
            line = rh.replace(line, src, target)
            # if target.strip() == "" :
            #   line  = line.replace( job['PTOKEN']+src+job['PTOKEN'], "" )
            #   not_found_variables.append(src)
          fout.write(line)
        # for var in list(set(not_found_variables)):
          # out.exception_msg(utils.Error.not_found, job['PTOKEN']+var+job['PTOKEN'])

    # VARIABLES LOG:
    variables_log_file=os.path.normpath(job['BASE_FOLDER']+"/"+job['VARIABLES_LOG_FILE'])
    with open(variables_log_file, "wt") as fout:
      for src, target in job.iteritems():
        fout.write('{0:30s} = {1:30s} \n'.format(src,target) )
    out.var("Variables LOG", variables_log_file)
    
  out.close_subsection()

out.close_section()

# Create Jobs file:
main.create_jobs_files( options.jobs_file, local_var, out)
          