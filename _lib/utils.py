import os
from enum import Enum

class Error(Enum):
  not_found = 1

class ReplaceHelper(object):
  """
    Replace default values with the simulation ones.
  """
  def __init__(self, sep=";"):
    self.sep = sep

  def replace(self, line, src, target, remove_default=True):
    """
      Replace a sting of the form :param: sep + :param: src + :param: sep with 
      target 
    """
    line = line.replace(self.sep+str(src)+self.sep, str(target))    
    if remove_default:
      val   = get_name_inside(line, "[[", "]]")
      line  = line.replace( "[[" +val+ "]]", "" )
    return line

  def replace_with_default_value(self, line, src):
    """
      Replace a sting of the form :param: sep + :param: src + :param: sep with 
      default value.
      If no default value is specified the variable will be removed.
    """
    begin = self.sep+src+self.sep+"[["
    end   = "]]"
    val   = get_name_inside(line, begin, end)
    if val != "":
      line  = line.replace( begin+val+end, val )
    else:
      line  = line.replace( self.sep+src+self.sep, "" )
    return line
    

class Output(object):
  
  def __init__(self, lenght=50):
    self.BAR=((lenght/2)*"==")+"="
    self.bar=((lenght/2)*"--")+"-"
    self.BaR=((lenght/2)*"-=")+"-"
    print "\n\n"
    print self.BAR

  def ASSERT(self, check, msg="", error_type=None):
    text = "\n\n" +self.BaR
    text += "\n  ERROR: "
    if error_type == Error.not_found :
      text += "`"+str(msg)+"` does not exist! "
    text += "\n" + self.BaR
    assert check, text
    
  def EXCEPTION(self, error, txt):
    if error == Error.not_found:
      print '\t{:>20} {:>3} {:12}'.format(str(txt), " -> ", "NOT FOUND") 
    
  def title(self, txt):
    print self.BaR
    print " " + str(txt)
    print self.BaR

  def close_section(self):
    print self.BAR

  def close_subsection(self):
    print self.bar
    
  def var(self,name, val):
    print '\t{:>20} {:>3} {:12}'.format(str(name), "  = ", str(val)) 

class ProcessEntry(object):

  def __init__(self, out, section=""):
    self.out = out
    self.section = section
    
  def process(self, text):
    return_text = text
    if return_text.find("PATH") > -1 :
      return_text = os.path.normpath(return_text)
    return_text = return_text.replace("@PWD@", os.getcwd())
    if self.section != "":
      return_text = return_text.replace("@SIMULATION@", self.section)
    while return_text.find("@ENV[") > -1 :
      env = return_text[return_text.find("@ENV[")+5:return_text.find("]@")]
      var = os.environ[env]
      return_text = return_text.replace("@ENV[" + str(env) + "]@", var)
    return return_text.strip()
    
class GetValFromConfParser(object):

  def __init__(self, out, config_parser, section):
    self.out = out
    self.config_parser = config_parser
    self.section = section
    self.PE = ProcessEntry(out, section)

  def get(self, name, output=False):
    val = self.config_parser.get(self.section, name)
    val = self.PE.process(val)
    if output:
      self.out.var(name, val)
    return val

class GetValFromDictionary(object):

  def __init__(self, out, dictionary):
    self.out = out
    self.dictionary = dictionary
    self.PE = ProcessEntry(out)
    
  def get(self, value, output=False):
    try:
      return_value=self.dictionary[value]
    except:
      return_value=""
    return_value = self.PE.process(return_value)
    if output:
      self.out.var(value, return_value)
    return return_value

def get_name_inside(  line, 
                      begin_container="(", 
                      end_container=")"):
    size = len(begin_container)
    start = line.find(begin_container)+size
    end = line.find(end_container, start)
    if end > -1 and start > -1:
      return line[start:end] 
    else :
      return ""
  
  