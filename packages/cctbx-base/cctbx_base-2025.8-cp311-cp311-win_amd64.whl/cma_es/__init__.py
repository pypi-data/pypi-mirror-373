from __future__ import absolute_import, division, print_function


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, '.'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import boost_adaptbx.boost.python as bp
cma_es_ext = bp.import_ext("cma_es_ext")
from cma_es_ext import *
