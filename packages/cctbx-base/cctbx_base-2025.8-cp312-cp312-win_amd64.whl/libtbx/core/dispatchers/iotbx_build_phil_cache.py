import os
import subprocess
import sys

from pathlib import Path

def run_command():
  import libtbx.core.dispatchers
  executable = Path(libtbx.core.dispatchers.__file__).parent / 'iotbx.build_phil_cache.bat'
  executable = str(executable.resolve())

  sys.exit(subprocess.call([executable, *sys.argv[1:]], shell=False))
