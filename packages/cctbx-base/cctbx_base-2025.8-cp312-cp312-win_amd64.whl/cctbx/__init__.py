from __future__ import absolute_import, division, print_function


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from libtbx.version import get_version

__version__ = get_version()

factor_kev_angstrom = 6.62607015 * 2.99792458 / 1.602176634
factor_ev_angstrom  = factor_kev_angstrom * 1000

# (ab)use miller extension to provide hendrickson_lattman constructors
_as_hendrickson_lattman = None
def hendrickson_lattman(*args, **kw):
  global _as_hendrickson_lattman
  if (_as_hendrickson_lattman is None):
    import cctbx.miller
    _as_hendrickson_lattman = cctbx.miller.as_hendrickson_lattman
  return _as_hendrickson_lattman(*args, **kw)
