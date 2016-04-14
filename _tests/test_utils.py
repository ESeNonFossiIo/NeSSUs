import sys
sys.path.append("./_lib/")
sys.path.append("./../_lib/")
from utils import *

def test_get_name_inside():
  # test1
  string = "val=[num]"
  assert get_name_inside(string, "[", "]") == "num"
  # test2
  string = "val=__VAL__[num]"
  assert get_name_inside(string, "__VAL__[", "]") == "num"
  # test3
  string = "val=__VAL__[num]"
  assert get_name_inside(string, "__VAL__[", "]") == "num"