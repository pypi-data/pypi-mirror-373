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

import wx
import os

from libtbx.version import get_version

__version__ = get_version()

global default_font_size

MAC_OS_X_MAVERICKS = False
if (wx.Platform == '__WXMSW__'):
  default_font_size = 9
elif (wx.Platform == '__WXMAC__'):
  default_font_size = 12
  os_version = os.uname()[2].split(".")
  if (int(os_version[0]) >= 13):
    MAC_OS_X_MAVERICKS = True
else :
  default_font_size = 11

class MouseWheelTransparencyMixin(object):
  """
  This mixin provides an event handler for passing the mouse wheel event to
  the parent, presumably a ScrolledPanel or similar.  For this to happen, the
  actual class must bind wx.EVT_MOUSEWHEEL to self.OnMouseWheel.
  """
  def OnMouseWheel(self, evt):
    parent = self.GetParent()
    evt.SetId(parent.GetId())
    evt.SetEventObject(parent)
    parent.GetEventHandler().ProcessEvent(evt)

def is_unicode_build():
  return (wx.PlatformInfo[2] == 'unicode')
