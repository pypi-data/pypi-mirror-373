from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import absolute_import, division, print_function
import iotbx.pdb
import mmtbx.model
import mmtbx.f_model
from iotbx import reflection_file_reader
import os
import libtbx.load_env
pdb_file = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/pdb/1yjp_h.pdb",
  test=os.path.isfile)
mtz_file = libtbx.env.find_in_repositories(
  relative_path="phenix_regression/reflection_files/1yjp.mtz",
  test=os.path.isfile)
assert (not None in [pdb_file, mtz_file])
# Read in the model file and create model object
pdb_inp = iotbx.pdb.input(file_name = pdb_file)
model = mmtbx.model.manager(model_input = pdb_inp)
# Get miller arrays for data and Rfree flags
miller_arrays = reflection_file_reader.any_reflection_file(file_name =
  mtz_file).as_miller_arrays()
for ma in miller_arrays:
  print(ma.info().label_string())
  if(ma.info().label_string()=="FOBS_X,SIGFOBS_X"):
    f_obs = ma
  if(ma.info().label_string()=="R-free-flags"):
    r_free_flags = ma
# Obtain a common set of reflections
f_obs, r_free_flags = f_obs.common_sets(r_free_flags)
r_free_flags = r_free_flags.array(data = r_free_flags.data()==0)
print(r_free_flags.data().count(True), r_free_flags.data().count(False))
fmodel = mmtbx.f_model.manager(
  f_obs          = f_obs,
  r_free_flags   = r_free_flags,
  xray_structure = model.get_xray_structure())
fmodel.update_all_scales()
print("r_work=%6.4f r_free=%6.4f"%(fmodel.r_work(), fmodel.r_free()))
fmodel.show(show_header=False, show_approx=False)
