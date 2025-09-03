"""
ironxl

IronXL for Python
"""
# imports
import sys
import os
import platform
import subprocess
import shlex
# metadata
__version__ = "2025.9.0.1"
__author__ = 'Iron Software'
__credits__ = 'Iron Software'
# determine root path for IronXL files
root = ""
native_package = ""
print('Attempting import of IronXL ' + __version__)
if platform.system() == "Windows":
   root = sys.prefix
   print('Checking directory "' + root +'"')
   if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
      root = os.path.join(sys.prefix, "localcache", "local-packages")
      print('Checking directory "' + root +'"')
   if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
      root = os.path.join(sys.prefix, "..", "..", "..")
      print('Checking directory "' + root +'"')
   # install .NET
   try:
      p = subprocess.Popen('powershell.exe -ExecutionPolicy RemoteSigned -file "'+os.path.join(root, "IronXLNet", "dotnet-install.ps1")+'" -Runtime dotnet -Version 6.0.0', stdout=sys.stdout)
      p.communicate()
   except:
      print('Warning! Failed to install .NET 6.0. Consider manually installing .NET 6.0 from https://dotnet.microsoft.com/en-us/download/dotnet/6.0')
elif platform.system() == "Linux":
   root = os.path.join(os.path.expanduser('~'), ".local")
   print('Checking directory "' + root +'"')
   if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
      root = "/usr/local"
      print('Checking directory "' + root +'"')
   if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
      root = os.path.join(sys.prefix, "..", "..", "..")
      print('Checking directory "' + root +'"')
   # install .NET
   try:
      subprocess.call(shlex.split(os.path.join(root, "IronXLNet", "dotnet-install.sh")+' -Runtime dotnet -Version 6.0.0'))
   except:
      print('Warning! Failed to install .NET 6.0. Consider manually installing .NET 6.0 from https://dotnet.microsoft.com/en-us/download/dotnet/6.0')
elif platform.system() == "Darwin":
   if "arm" in platform.processor().lower():
      root = sys.prefix
   else:
      root = sys.prefix
   print('Checking directory "' + root +'"')
   if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
      root = "/opt/homebrew"
      print('Checking directory "' + root +'"')
   if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
      root = "/usr/local"
      print('Checking directory "' + root +'"')
   # install .NET
   try:
      subprocess.call(shlex.split(os.path.join(root, "IronXL", "dotnet-install.sh")+' -Runtime dotnet -Version 6.0.0'))
   except:
      print('Warning! Failed to install .NET 6.0. Consider manually installing .NET 6.0 from https://dotnet.microsoft.com/en-us/download/dotnet/6.0')
if not os.path.exists(os.path.join(root, "IronXLNet", "IronXL.dll")):
  raise Exception("Failed to locate IronXL.dll at '" + root +  "/IronXLNet'. Please see https://ironxl.com/ for more information")
print('IronXL detected root Python package directory of ' + root + '/IronXLNet')
# load .NET
from pythonnet import load
load("coreclr")
import clr
# import ironpdf .net assembly
sys.path.append(os.path.join(root, "IronXLNet"))
clr.AddReference("System.Collections")
clr.AddReference(os.path.join(root, "IronXLNet", "IronXL.dll"))
# import .net types
from System.Collections.Generic import IEnumerable
from System.Collections.Generic import List
from System import DateTime
from IronXL import *
from IronXL.Styles import *
from IronXL.Options import *
from IronXL.Printing import *
from IronXL.Drawing.Charts import *
from IronSoftware.Drawing import *
from IronXL.Formatting.Enums import *
# HELPER METHODS
def ToPage(item):
   """
   Converts the specified integer into a page index for IronPdf
   """
   output = List[int]()
   output.Add(item)
   return output
   
def ToPageList(list):
   """
   Converts the specified list of integers into a list of page indices for IronPdf
   """
   output = List[int]()
   for i in range(len(list)):
      output.Add(list[i])
   return output
   
def ToPageRange(start,stop):
   """
   Creates a list of page indices for IronPdf using the specified start and stop index
   """
   output = List[int]()
   for i in range(start,stop):
      output.Add(i)
   return output

def Now():
   """
   Returns the current date and time
   """
   return DateTime.Now