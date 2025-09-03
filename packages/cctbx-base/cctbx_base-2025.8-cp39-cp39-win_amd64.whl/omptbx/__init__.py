from __future__ import absolute_import, division, print_function


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import ctypes
    import os
    import platform
    import sys
    libs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))
    is_conda_cpython = platform.python_implementation() == 'CPython' and (hasattr(ctypes.pythonapi, 'Anaconda_GetVersion') or 'packaged by conda-forge' in sys.version)
    if sys.version_info[:2] >= (3, 8) and not is_conda_cpython or sys.version_info[:2] >= (3, 10):
        if os.path.isdir(libs_dir):
            os.add_dll_directory(libs_dir)
    else:
        load_order_filepath = os.path.join(libs_dir, '.load-order-cctbx_base-2025.8')
        if os.path.isfile(load_order_filepath):
            import ctypes.wintypes
            with open(os.path.join(libs_dir, '.load-order-cctbx_base-2025.8')) as file:
                load_order = file.read().split()
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel32.LoadLibraryExW.restype = ctypes.wintypes.HMODULE
            kernel32.LoadLibraryExW.argtypes = ctypes.wintypes.LPCWSTR, ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD
            for lib in load_order:
                lib_path = os.path.join(os.path.join(libs_dir, lib))
                if os.path.isfile(lib_path) and not kernel32.LoadLibraryExW(lib_path, None, 8):
                    raise OSError('Error loading {}; {}'.format(lib, ctypes.FormatError(ctypes.get_last_error())))


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import boost_adaptbx.boost.python as bp
ext = bp.import_ext("omptbx_ext")
from omptbx_ext import *

import libtbx.introspection

class environment(object):

  def num_threads(self):
    return omp_get_max_threads()
  def set_num_threads(self, n):
    omp_set_num_threads(n)
    return self
  num_threads = property(
    num_threads, set_num_threads,
    doc="Number of threads to distribute the work over")

  def dynamic(self):
    return omp_get_dynamic()
  def set_dynamic(self, flag):
    omp_set_dynamic(int(flag))
    return self
  dynamic = property(
    dynamic, set_dynamic,
    doc="Whether the number of threads is dynamically allocated")

  def nested(self):
    return omp_get_nested()
  def set_nested(self, flag):
    omp_set_nested(int(flag))
    return self
  nested = property(
    nested, set_nested,
    doc="Whether nested parallelism is enabled")

  def is_nested_available(self):
    try:
      saved = self.nested
      self.nested = True
      if self.nested: result = True
      else: result = False
      return result
    finally:
      self.nested = saved
  is_nested_available = property(
    is_nested_available,
    doc="Whether nested parallelism is available at all")

  def num_procs(self):
    return omp_get_num_procs()
  num_procs = property(
    num_procs, doc="Number of available processors")

env = environment()
env.dynamic = False
env.num_threads = libtbx.introspection.number_of_processors()
