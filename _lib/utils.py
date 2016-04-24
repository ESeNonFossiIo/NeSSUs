"""
  Library used to simplify the code of `MaJOrCA.py`.
"""

import os
import re
import sys

# Add path to PUlSe and this module:
sys.path.append("./_modules/PUlSe/lib/")
sys.path.append("./../_modules/PUlSe/lib/")

import PUlSe_string as pstring

class Error(object):
  """ Class used to deal with errors.  
  
    Members: 
      not_found (int): Error used when a file or more generally 
      an object is not found.
  """
  not_found = 1

class ReplaceHelper(object):
  """
    Toolbox of utilities to replace words in a string.
  """
  
  def __init__(self, sep=";"):
    """ Constructor.
    
      Args:
        sep (char): char used to separe different entries.
    """
    self.sep = sep

  def replace(self, line, src, target, remove_default=True):
    """ Replace `src` with `target` in `line`.

      Extended description of function.

      Args:
          line (str): Text where `src` will be replaced by `target`.
          src (str): Old tex.
          target (str): New text.
          remove_default (bool): Remove default value.

      Returns:
          string: `text` with `src` replaced by `target`.
    """
    line = line.replace(self.sep+str(src)+self.sep, str(target))    
    if remove_default:
      val   = pstring.get_name_inside(line, "[[", "]]")
      line  = line.replace( "[[" +val+ "]]", "" )
    return line

  def replace_with_default_value(self, line, src):
    """ Replace `src` with the `default value` in `line`.

      Extended description of function.

      Args:
          line (str): Text where `src` will be replaced by the `default value`.
          src (str): Old tex.

      Returns:
          string: `text` with `src` replaced by the `default value`.
    """
    begin = self.sep+src+self.sep+"[["
    end   = "]]"
    val   = pstring.get_name_inside(line, begin, end)
    if val != "":
      line  = line.replace( begin+val+end, val )
    else:
      line  = line.replace( self.sep+src+self.sep, "" )
    return line
    

class Output(object):
  """
    Toolbox of utilities for the output.
  """
  
  def __init__(self, lenght=50):
    """ Constructor.
    
      Args:
          lenght (int): lenght of the output line.
    """
    self.BAR=((lenght/2)*"==")+"="
    self.bar=((lenght/2)*"--")+"-"
    self.BaR=((lenght/2)*"-=")+"-"
    print "\n\n"
    print self.BAR

  def assert_msg(self, check, msg="", error_type=None):
    """Assert.
      
      This metod is used to handle assert messages.

      Args:
        check (bool): Value to satisfy to pass the test.
        msg (str): Message to print.
        error_type (Error): Error give.
    """
    text = "\n\n" +self.BaR
    text += "\n  ERROR: "
    if error_type == Error.not_found :
      text += "`"+str(msg)+"` does not exist! "
    text += "\n" + self.BaR
    assert check, text

  @staticmethod
  def exception_msg(error, txt):
    """ Exception message.
      
      Args:
        error (Error): Kind of error.
        txt (str): Text of the message.
    """
    if error == Error.not_found:
      print '\t{0:>20} {1:>3} {2:12}'.format(str(txt), " -> ", "NOT FOUND") 

  @staticmethod
  def print_dictionary(dictionary):
    """ Print all entries of a dictionary.
      
      Args:
        dictionary (dict): Dictionary to print.
    """
    for key in dictionary:
      print '\t{0:>20} {1:>3} {2:12}'.format(key, " = ", dictionary[key]) 
    
  def title(self, txt):
    """ Title.
      
      Args:
        txt (str): Text of the title.
    """
    print self.BaR
    print " " + str(txt)
    print self.BaR

  def section(self, txt):
    """ Section.
      
      Args:
        txt (str): Text of the section.
    """
    print self.bar
    print " " + str(txt)
    print self.bar
    
  def close_section(self):
    """ Close a section.
      
      Statement used to close a section.
    """
    print self.BAR

  def close_subsection(self):
    """ Close a subsection.

      Statement used to close a subsection.
    """
    print self.bar

  @staticmethod
  def var(name, val):
    """ Print a variable.

      Args:
        name (str): Name of the variable.
        val (str): Value of the variable.
    """
    print '\t{0:>20} {1:>3} {2:12}'.format(str(name), "  = ", str(val)) 

class ProcessEntry(object):
  """
    Toolbox to process entries.
  """

  def __init__(self, out, section=""):
    """ Constructor.
    
      Args:
          out (Output): `Output` objcet used to show the results.
          section (str): name of the working section.
    """
    self.out = out
    self.section = section

  def process_a_simulation(self, simulation):
    """ Process a simulation.

      Args:
        simulaiton (list of dictionaries): Simulation to preocess.
    """
    for entry in simulation:
      for key in entry:
        entry[key] = self.process(entry[key])
  
  def process(self, text):
    """ Process a text.

      Args:
        text (str): Text to process and format.

      Returns:
        string: Processed text.
    """
    return_text = text
    return_text = return_text.replace("@PWD@", os.getcwd())
    if self.section != "" and self.section != "GENERAL":
      return_text = return_text.replace("@SIMULATION@", self.section)
      return_text = return_text.replace("@HOME@", str(os.path.dirname(os. path.abspath(__file__))[:-4]) )
    while return_text.find("@ENV[") > -1 :
      env = return_text[return_text.find("@ENV[")+5:return_text.find("]@")]
      var = os.environ[env]
      return_text = return_text.replace("@ENV[" + str(env) + "]@", var)
    if return_text.find("//") > 0 :
      return_text = os.path.normpath(return_text)
    return return_text.strip()
    
class GetValFromConfParser(object):
  """
    Get value from a `ConfParser`.
  """

  def __init__(self, out, config_parser, section):
    """ Constructor.
      
      Args:
        out (Output): Output.
        config_parser (ConfParser): Dictionary where variables are stored.
        section (str): Section of `config_parser` where variables are stored.
    """
    self.out = out
    self.config_parser = config_parser
    self.section = section
    self.PE = ProcessEntry(out, section)

  def get(self, name, output=False):
    """ Get a value.

      Get a value from `section` of `config_parser`.

      Args:
        name (str): Name of the variable.
        output (bool): Print the name of the variable and its value.
        
      Returns:
        string: value associated to `name`.
    """
    val = self.config_parser.get(self.section, name)
    val = self.PE.process(val)
    if output:
      self.out.var(name, val)
    return val

class GetValFromDictionary(object):
  """
    Get value from a `Dictionary`.
  """

  def __init__(self, out, dictionary):
    """ Constructor.
      
      Args:
        out (Output): Output.
        dictionary (dict): Dictionary where variables are stored.
    """
    self.out = out
    self.dictionary = dictionary
    self.PE = ProcessEntry(out)
    
  def get(self, name, output=False):
    """ Get a value.

      Get a value from `dictionary`.

      Args:
        name (str): Name of the variable.
        output (bool): Print the name of the variable and its value.

      Returns:
        string: value associated to `name`.
    """
    try:
      value=self.dictionary[name]
    except KeyError:
      value=""
    value = self.PE.process(value)
    if output:
      self.out.var(name, value)
    return value

class EvalExpression(object):
  """
    Class used to evaluate a string.
  """
  def __init__(self, text, delimiters_start="@EVAL@[", delimiters_end="]", sep="||"):
    """ Constructor.
    
      Args:
        text (str): text to evaluate (delimiters included).
        delimiters_start (str): This delimiter is the one before the value to capture..
        delimiters_end (str): This delimiter is the one after the value to capture.
    """
    self.expression = ""
    self.delimiters_start = delimiters_start
    self.delimiters_end = delimiters_end
    self.sep = sep
    self.text = text

  def grep_expression(self):
    """ Get the expression to evaluate.

      Get the expression contained between `delimiters_start` and `delimiters_end`.
      
      Returns:
        string: text to evaluate.
    """
    self.expression = pstring.get_name_inside( self.text, self.delimiters_start, self.delimiters_end)

  def evaluate_for_cycle(self):
    """ Evaluate a for-cycle expression.

      Assert the expression is a for-cycle and the return its evaluation.
      Exaple:
      @EVAL@[i for i in xrange(3)] -> 0 || 1 || 2
      
      Returns:
        string: Evaluation of the for-cycle.
    """
    self.grep_expression()
    
    values = []
    try:
      from asteval import Interpreter
      aeval = Interpreter()
      values = aeval("["+str(self.expression)+"]")

      if not values:
        raise ImportError
      
      values_string = ""
      for i in xrange(len(values)-1):
        values_string += str(values[i]) + " " + self.sep + " "
      values_string += str(values[-1])
      
      return values_string.strip()

    except ImportError:
      print  " ERROR: There are problems with `aeval`. "
      return self.grep_expression()
    
  def __call__(self):
    """ __call__ method.
      
      Returns:
        string: The evaluation of the text.
    """
    if self.text.find(self.delimiters_start) > -1 and self.text.find(self.delimiters_end) > -1:
      return self.evaluate_for_cycle()
    else:
      return self.text
    
    
  
