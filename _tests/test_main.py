import sys
sys.path.append("./_lib/")
sys.path.append("./../_lib/")

import utils
import os
import main

# Add path to PUlSe and this module:
sys.path.append("./_modules/PUlSe/lib/")
sys.path.append("./../_modules/PUlSe/lib/")
import PUlSe_bash_utilities as pbash

def test_cp():
  """
    Test CP Class.
  """
  cp = main.CP("../_conf/system.conf")
  dictionary = dict()

  assert cp["script"]["DIRS"]
  
  cp.fill(dictionary, "script")
  assert True
  
  cp.get_sections()
  assert True
  
  cp.get_options("script")
  assert True
  
  cp.remove_section("script")
  assert True

def test_replace_entry_using_dictionary():
  """ 
    Test replace_entry_using_dictionary Function.
  """
  dictionary = dict()
  dictionary["PTOKEN"] = "__"
  dictionary["TEST"] = "@"
  dictionary["substitute"] = "__TEST__"

  main.replace_entry_using_dictionary(dictionary, "substitute")
  
  assert  dictionary["substitute"] == dictionary["TEST"]

def test_replace_line_using_dictionary(): 
  """ 
    Test replace_line_using_dictionary Function.
  """
  rh = utils.ReplaceHelper("||")
  dictionary = dict()
  dictionary["NULL_TOKES"] = "|"
  dictionary["test1"] = "|"
  dictionary["test2"] = "-"
  dictionary["TEST"] = "-TEST-"
  
  line = "|"
  line = main.replace_line_using_dictionary(dictionary, line, rh)
  assert True
  
  line = "-"
  line = main.replace_line_using_dictionary(dictionary, line, rh)
  assert True
  
  line = "@TEST@"
  line = main.replace_line_using_dictionary(dictionary, line, rh)
  assert line == "-TEST-"

def test_generate_new_conf_file():
  """
    Test generate_new_conf_file Function.
  """
  out = utils.Output(100)

  new_file = ""
  old_file = "tmp_old.txt"
  pbash.rm(old_file)
  pbash.touch(old_file)

  assert not main.generate_new_conf_file(new_file, old_file, out)
  
  new_file = "tmp.txt"
  pbash.rm(new_file)

  assert main.generate_new_conf_file(new_file, old_file, out)
  assert main.generate_new_conf_file(new_file, old_file, out)

  pbash.rm(new_file)
  pbash.rm(old_file)

def test_sh_pbs_mode():
  """
    Test sh_pbs_mode Function.
  """
  test = dict()
  test["MODE"] = "sh"

  main.sh_pbs_mode(test)
  assert test["PBS"] == ""

  result  = "\n#PBS -N PBS_NAME"
  result += "\n#PBS -l walltime=PBS_WALLTIME"
  result += "\n#PBS -l PBS_NODES"
  result += "\n#PBS -q PBS_QUEUE"
  result += "\n#PBS -M PBS_MAIL"
  result += "\n#PBS -m abe"
  result += "\n"
  
  test["MODE"] = "pbs"
  test["NULL_TOKES"] = "----"
  
  test["PBS_NAME"] = "PBS_NAME"
  test["PBS_WALLTIME"] = "PBS_WALLTIME"
  test["PBS_NODES"] = "PBS_NODES"
  test["PBS_QUEUE"] = "PBS_QUEUE"
  test["PBS_MAIL"] = "PBS_MAIL"
  main.sh_pbs_mode(test)
  assert test["PBS"] == result
  
  test["PBS_NAME"] = "----"
  test['PRM_FILENAME'] = "PBS_NAME"
  main.sh_pbs_mode(test)
  assert test["PBS"] == result
