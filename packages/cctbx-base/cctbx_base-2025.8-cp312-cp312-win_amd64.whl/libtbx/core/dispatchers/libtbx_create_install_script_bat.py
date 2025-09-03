import os
import subprocess
import sys

from pathlib import Path

def run_command():
  import libtbx.core.dispatchers
  executable = Path(libtbx.core.dispatchers.__file__).parent / 'libtbx.create_install_script_bat.bat'
  executable = str(executable.resolve())

  sys.exit(subprocess.call([executable, *sys.argv[1:]], shell=False))
