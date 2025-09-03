import os
import subprocess
import sys

from pathlib import Path

def run_command():
  import libtbx.core.dispatchers
  executable = Path(libtbx.core.dispatchers.__file__).parent / 'libtbx.raise_exception_for_testing.bat'
  executable = str(executable.resolve())

  sys.exit(subprocess.call([executable, *sys.argv[1:]], shell=False))
