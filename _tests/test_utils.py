import sys
sys.path.append("./_lib/")
sys.path.append("./../_lib/")
from utils import *
import os

# Enum Error:
def test_Error():
  assert Error.not_found.value == 1

# Class ReplaceHelper:
def test_replace_helper():
  # Test for ReplaceHelper.replace
  string = "__TEST__[[]]"
  rh = ReplaceHelper("__")
  string = rh.replace(string, "TEST", "NEW")
  assert string == "NEW"
  # Test for ReplaceHelper.replace_with_default_value
  string = "__TEST__[[NEW]]"
  string = rh.replace_with_default_value(string,"TEST")
  assert string == "NEW"
  string = "__TEST__"
  string = rh.replace_with_default_value(string,"TEST")
  print "-->" + string
  assert string == ""

# Class Output:
def test_output():
  out=Output(5)
  assert out.BAR == "====="
  assert out.bar == "-----"
  assert out.BaR == "-=-=-"

  out.ASSERT(True, error_type=Error.not_found)
  out.ASSERT(True)
  assert True

  out.EXCEPTION(Error.not_found, "filename")
  assert True

  out.title("Title")
  assert True

  out.close_section()
  assert True

  out.close_subsection()
  assert True

  out.var("name","val")
  assert True

# Class ProcessEntry
def test_process_entry():
  out = Output(5)
  pe = ProcessEntry(out, section="section")
  
  string="@PWD@"
  assert pe.process(string) == os.getcwd().strip()
  string="PATH"
  assert True
  string="@SIMULATION@"
  assert pe.process(string) == "section"
  string="@ENV[HOME]@"
  assert pe.process(string) == os.environ['HOME']

# Class GetValFromConfParser
import ConfigParser
def test_GetValFromConfParser():
  out = Output(5)
  config = ConfigParser.RawConfigParser()
  config.add_section('Section1')
  config.set('Section1', 'item', 'val')
  extractor = GetValFromConfParser(out, config, "Section1")
  assert extractor.get("item") == "val"
  assert extractor.get("item", True) == "val"

# Class GetValFromDictionary
def test_GetValFromDictionary():
  out = Output(5)
  dictionary = dict()
  dictionary['item'] = "val"
  extractor = GetValFromDictionary(out, dictionary)
  assert extractor.get("item") == "val"
  assert extractor.get("item", True) == "val"
  
# Function get_name_inside:
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
  # test4
  string = "val=__VAL__"
  assert get_name_inside(string, "__VAL__[", "]") == ""

