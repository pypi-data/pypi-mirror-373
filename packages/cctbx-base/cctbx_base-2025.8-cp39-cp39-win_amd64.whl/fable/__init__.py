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

try:
  import boost_adaptbx.boost.python as bp
except Exception:
  ext = None
else:
  ext = bp.import_ext("fable_ext", optional=True)
from six.moves import range

# compare with fem/utils/string.hpp
def py_fem_utils_unsigned_integer_scan(code, start=0, stop=-1):
  i = start
  while (i < stop):
    c = code[i]
    if (not c.isdigit()): break
    i += 1
  if (i == start): return -1
  return i

# compare with ext.cpp
def py_ext_get_code_stop(code, stop):
  len_code = len(code)
  if (stop < 0): return len_code
  assert stop <= len_code
  return stop

# compare with ext.cpp
def py_unsigned_integer_scan(code, start=0, stop=-1):
  return py_fem_utils_unsigned_integer_scan(
    code=code, start=start, stop=py_ext_get_code_stop(code, stop))

# compare with ext.cpp
def py_floating_point_scan_after_exponent_char(code, start=0, stop=-1):
  code_stop = py_ext_get_code_stop(code=code, stop=stop)
  i = start
  if (i < code_stop):
    c = code[i]
    if (c == '+' or c == '-'):
      i += 1
    return py_unsigned_integer_scan(code=code, start=i, stop=stop)
  return -1

# compare with ext.cpp
def py_floating_point_scan_after_dot(code, start=0, stop=-1):
  code_stop = py_ext_get_code_stop(code=code, stop=stop)
  i = py_unsigned_integer_scan(code=code, start=start, stop=stop)
  if (i < 0): i = start
  if (i < code_stop):
    c = code[i]
    if (c == 'e' or c == 'd'):
      return py_floating_point_scan_after_exponent_char(
        code=code, start=i+1, stop=stop)
  return i

# compare with ext.cpp
def py_identifier_scan(code, start=0, stop=-1):
  code_stop = py_ext_get_code_stop(code=code, stop=stop)
  i = start
  if (i < code_stop):
    c = code[i]; i += 1
    if ((c < 'a' or c > 'z') and c != '_'): return -1
    while (i < code_stop):
      c = code[i]; i += 1
      if (    (c < 'a' or c > 'z')
          and (c < '0' or c > '9') and c != '_'): return i-1
    return i
  return -1

def py_find_closing_parenthesis(code, start=0, stop=-1):
  code_stop = py_ext_get_code_stop(code=code, stop=stop)
  n_inner = 0
  for i in range(start, code_stop):
    c = code[i]
    if (c == ')'):
      if (n_inner == 0): return i
      n_inner -= 1
    elif (c == '('):
      n_inner += 1
  return -1

if (ext is not None):
  from fable_ext import *
else:
  unsigned_integer_scan = py_unsigned_integer_scan
  floating_point_scan_after_exponent_char = \
    py_floating_point_scan_after_exponent_char
  floating_point_scan_after_dot = py_floating_point_scan_after_dot
  identifier_scan = py_identifier_scan
  find_closing_parenthesis = py_find_closing_parenthesis

class SemanticError(Exception): pass
