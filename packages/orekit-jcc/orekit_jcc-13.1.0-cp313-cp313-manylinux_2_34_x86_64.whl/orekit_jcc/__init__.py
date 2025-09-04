
import os
import sys
if sys.platform == 'win32':
  from .windows import add_jvm_dll_directory_to_path
  add_jvm_dll_directory_to_path('client')
from . import _orekit_jcc

__module_dir__ = os.path.abspath(os.path.dirname(__file__))

class JavaError(Exception):
  def getJavaException(self):
    return self.args[0]
  def __str__(self):
    writer = StringWriter()
    self.getJavaException().printStackTrace(PrintWriter(writer))
    return "\n".join((str(super(JavaError, self)), "    Java stacktrace:", str(writer)))

class InvalidArgsError(Exception):
  pass

_orekit_jcc._set_exception_types(JavaError, InvalidArgsError)

VERSION = "13.1.0"
CLASSPATH = [os.path.join(__module_dir__, "orekit-jcc-13.1.0.jar"), os.path.join(__module_dir__, "orekit-13.0.3.jar"), os.path.join(__module_dir__, "orekit-tools-2.1.jar"), os.path.join(__module_dir__, "hipparchus-core-4.0.1.jar"), os.path.join(__module_dir__, "hipparchus-filtering-4.0.1.jar"), os.path.join(__module_dir__, "hipparchus-fitting-4.0.1.jar"), os.path.join(__module_dir__, "hipparchus-geometry-4.0.1.jar"), os.path.join(__module_dir__, "hipparchus-ode-4.0.1.jar"), os.path.join(__module_dir__, "hipparchus-optim-4.0.1.jar"), os.path.join(__module_dir__, "hipparchus-stat-4.0.1.jar")]
CLASSPATH = os.pathsep.join(CLASSPATH)
_orekit_jcc.CLASSPATH = CLASSPATH
_orekit_jcc._set_function_self(_orekit_jcc.initVM, _orekit_jcc)

from ._orekit_jcc import *
from java.io import PrintWriter, StringWriter

