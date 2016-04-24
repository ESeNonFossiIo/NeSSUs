"""
  Divide the main of MaJOrCA in order to improve test and simplify the 
  code.
"""

import os
import sys
from shutil import copyfile
import ConfigParser

# Add path to PUlSe and this module:
pulse_dir="./_modules/PUlSe/lib/"
sys.path.append(pulse_dir)
import PUlSe_string as pstring

class CP(object):
  """ Generalize ConfigParser Class.

  Generalize ConfigParser Class with new mothods.
  """
  def __init__(self, filename):
    """ Constructor.
    
      Args:
          filename (str): Name of the conf file used to initialize the
            underling ConfigParser.  
    """
    assert filename != "", " ERROR: No filename given!"
    self.filename = filename
    self.config_parser = ConfigParser.ConfigParser()
    self.config_parser.optionxform=str #case sensitive
    self.config_parser.read(self.filename)
    self.sections = self.config_parser.sections()
  
  def __getitem__(self, section):
    """ __getitem__ method.
    
      Args:
          dictionary (dict): Names and value to substitute in line. 
          line (str): String to modify.  
          rh (ReplaceHelper): ReplaceHelper used to replace and fix tests.

      Returns:
          string: Returb True if a new file is generated or already exists.
            False otherwise.
    """
    dictionary = dict()
    for obj in self.config_parser.options(section):
      dictionary[obj] = self.config_parser.get(section, obj)
    return dictionary

  def fill(self, dictionary, section):
    """ Fill a dictionary using ConfigParser.

      Fill a dictionary using ConfigParser.

      Args:
          dictionary (dict): Dictionary to fill. 
          section (str): Name of the section to use to fill the dictionary. 
    """
    pstring.fill_dictionary_with_config_parser( dictionary,
                                                self.config_parser, 
                                                section)
  def remove_section(self, section):
    """ Remove a section from the sections list.

      Remove a section from the sections list.

      Args:
        section (str): Name of the section to remove. 
    """
    self.sections.remove(section)

  def get_sections(self):
    """ Get sections list.

      Get sections list.
    """
    return self.sections

  def get_options(self, section):
    """ Get oprion list relative to a section.

      Get oprion list relative to a section.

      Args:
        section (str): Name of the section the options. 
    """
    return self.config_parser.options(section)

def replace_entry_using_dictionary(dictionary, entry):
  """ Replace in a dictionary entry the variables defined in the dictionary
      with relative values.

    Replace in a dictionary entry the variables defined in the dictionary
    with relative values.

    Args:
        dictionary (dict): Names and value to substitute in line. 
        entry (str): String to modify.  
  """
  for src, target in dictionary.iteritems(): 
    dictionary[entry] = dictionary[entry].replace( dictionary['PTOKEN']+str(src)+dictionary['PTOKEN'], target)

def replace_line_using_dictionary(dictionary, line, rh): 
  """ Replace in a line variables defined in the dictionary with relative
      values.

    Replace in a line variables defined in the dictionary with relative
    values.

    Args:
        dictionary (dict): Names and value to substitute in line. 
        line (str): String to modify.  
        rh (ReplaceHelper): ReplaceHelper used to replace and fix tests.

    Returns:
        string: Returb True if a new file is generated or already exists.
          False otherwise.
  """
  for src, target in dictionary.iteritems():
    if target != dictionary["NULL_TOKES"] :  
      line = rh.replace(line, src, target)
    else:
      line = rh.replace_with_default_value(line, src)
    line = line.replace("@"+str(src)+"@", str(target))
  return line


def generate_new_conf_file( new_file,
                            old_file,
                            output ):
  """ Check and possibly generate a new conf file.

    Look for a pattern among directories and make/return the next avaible 
    directory.

    Args:
        new_file (str): Name of the new file to create. 
        old_file (str): Name of the old file to copy.  
        output (Output): Name of the Output.

    Returns:
        bool: Return True if a new file is generated or already exists.
          False otherwise.
  """
  if new_file != "":
    output.assert_msg(  os.path.isfile(old_file), 
                        old_file, "existence" )
    if os.path.isfile(new_file):
      output.assert_msg( os.path.isfile(new_file), 
                         new_file, "existence" )
      return True
    copyfile(old_file, new_file)
    output.close_section()
    return True
  else:
    return False

def sh_pbs_mode(job):
  """ Process sh and pbs istruction for job.

    Process all instruction relative to sh and pbs relative to job and
    return (is pbs) all information for the qsub script

    Args:
        job (dict): Name of the dictionary to analyze. 
  """
  if job["MODE"] == "sh":
    job["PBS"] = ""
  elif job["MODE"] == "pbs":
    job["PBS"] = "\n#PBS -N "
    if job["PBS_NAME"] != job["NULL_TOKES"] :
      job["PBS"] += job["PBS_NAME"]
    else:
      job["PBS"] += job['PRM_FILENAME'].replace(".prm", "")
    if job["PBS_WALLTIME"] != job["NULL_TOKES"] :
      job["PBS"] += "\n#PBS -l walltime=" + job["PBS_WALLTIME"]
    if job["PBS_NODES"] != job["NULL_TOKES"] :
      job["PBS"] += "\n#PBS -l " + job["PBS_NODES"]
    if job["PBS_QUEUE"] != job["NULL_TOKES"] :
      job["PBS"] += "\n#PBS -q " + job["PBS_QUEUE"] 
    if job["PBS_MAIL"] != job["NULL_TOKES"] :
      job["PBS"] += "\n#PBS -M " + job["PBS_MAIL"]
      job["PBS"] +=  "\n#PBS -m abe"
    job["PBS"] +="\n"

def create_jobs_files( bool_create, simulations, out):
  """ Create script to launch all jobs.

    Create script to launch all jobs.

    Args:
        bool_create (bool): State if create jobs files. 
        simulations (dict of list of dict): Contain all data of simulations.  
        out (Output): Output file used to print logs.
  """
  if bool_create:
    out.title("JOBS FILE ")
    for s in simulations:
      with open(simulations[s][0]["LAUNCH_JOBS_NAME"]+".sh", "wt") as fout:
        out.section(" Generate: " + simulations[s][0]["LAUNCH_JOBS_NAME"]+".sh")
        fout.write("#!/bin/bash\n\n")
        for simulation in simulations[s]:
          job = simulation
          if job["MODE"] == "sh":
            fout.write("bash ")
          else:
            fout.write("qsub ") 
          fout.write(job['JOBS_FOLDER_NAME']+"/"+job['JOBS_NAME']+"\n")