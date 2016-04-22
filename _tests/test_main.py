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
