import os

class Output(object):
  
  def __init__(self, lenght=50):
    self.BAR=(lenght*"=")+"="
    self.bar=(lenght*"-")+"-"
    self.BaR=((lenght/2)*"-=")+"-"
    print "\n\n"
    print self.BAR

  def ASSERT(self, check, msg="", error_type=""):
    text = "\n\n" +self.BaR
    text += "\n  ERROR: "
    if error_type == "existence" :
      text += "`"+str(msg)+"` does not exist! "
    text += "\n" + self.BaR
    assert check, text
    
    
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
    return_text = text.replace("@HOME@", os.getcwd())
    if self.section != "":
      return_text = text.replace("@SIMULATION@", self.section)
    while return_text.find("@ENV[") > -1 :
      env = return_text[return_text.find("@ENV[")+5:return_text.find("]@")]
      var = os.environ[env]
      return_text = return_text.replace("@ENV[" + str(env) + "]@", var)
    return return_text
    
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

