import sys
sys.path.append("./_lib/")
sys.path.append("./../_lib/")
import utils
import os

# Enum Error:
def test_error():
  assert utils.Error.not_found.value == 1

# Class ReplaceHelper:
def test_replace_helper():
  # Test for ReplaceHelper.replace
  string = "__TEST__[[]]"
  rh = utils.ReplaceHelper("__")
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
  out=utils.Output(5)
  assert out.BAR == "====="
  assert out.bar == "-----"
  assert out.BaR == "-=-=-"

  out.assert_msg(True, error_type=utils.Error.not_found)
  out.assert_msg(True)
  assert True

  out.exception_msg(utils.Error.not_found, "filename")
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
  out = utils.Output(5)
  pe = utils.ProcessEntry(out, section="section")
  
  string="@PWD@"
  assert pe.process(string) == os.getcwd().strip()
  string="PATH"
  string=pe.process(string)
  assert True
  string="@SIMULATION@"
  assert pe.process(string) == "section"
  string="@ENV[HOME]@"
  assert pe.process(string) == os.environ['HOME']

# Class GetValFromConfParser
import ConfigParser
def test_get_val_from_conf_parser():
  out = utils.Output(5)
  config = ConfigParser.RawConfigParser()
  config.add_section('Section1')
  config.set('Section1', 'item', 'val')
  extractor = utils.GetValFromConfParser(out, config, "Section1")
  assert extractor.get("item") == "val"
  assert extractor.get("item", True) == "val"

# Class GetValFromDictionary
def test_get_val_from_dictionary():
  out = utils.Output(5)
  dictionary = dict()
  dictionary['item'] = "val"
  extractor = utils.GetValFromDictionary(out, dictionary)
  assert extractor.get("item") == "val"
  assert extractor.get("not") == ""
  assert extractor.get("item", True) == "val"
  
# Function get_name_inside:
def test_get_name_inside():
  # test1
  string = "val=[num]"
  assert utils.get_name_inside(string, "[", "]") == "num"
  # test2
  string = "val=__VAL__[num]"
  assert utils.get_name_inside(string, "__VAL__[", "]") == "num"
  # test3
  string = "val=__VAL__[num]"
  assert utils.get_name_inside(string, "__VAL__[", "]") == "num"
  # test4
  string = "val=__VAL__"
  assert utils.get_name_inside(string, "__VAL__[", "]") == ""

