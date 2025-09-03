from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import absolute_import, division, print_function
import iotbx.pdb
import iotbx.mrcfile
import mmtbx.model
import mmtbx.real_space
from scitbx.array_family import flex
from cctbx.development import random_structure
from cctbx import sgtbx
from cctbx import maptbx
# Create random structure
xrs = random_structure.xray_structure(
  space_group_info = sgtbx.space_group_info("P-1"),
  elements         = ["C"]*15,
  unit_cell        = (10, 20, 30, 50, 60, 80))
# Create model object
model = mmtbx.model.manager.from_sites_cart(
  sites_cart       = xrs.sites_cart(),
  crystal_symmetry = xrs.crystal_symmetry(),
  resname          = 'DUM')
# Write it into PDB file
from iotbx.data_manager import DataManager
dm = DataManager()
dm.set_overwrite(True)
output_file_name = dm.write_model_file(model, "model.pdb")
print("Output file name: %s" %(output_file_name))
  # Read the model file
pdb_inp = iotbx.pdb.input(file_name = "model.pdb")
model = mmtbx.model.manager(model_input = pdb_inp)
xrs = model.get_xray_structure()
# Calculate structure factors at given resolution.
f_calc = xrs.structure_factors(d_min = 2.0).f_calc()
# Write them down as MTZ file
mtz_dataset = f_calc.as_mtz_dataset(column_root_label="F-calc")
mtz_object = mtz_dataset.mtz_object()
mtz_object.write(file_name = "f_calc.mtz")
# Convert Fcalc into real map (just do FFT)
fft_map = f_calc.fft_map(resolution_factor=1./4)
fft_map.apply_sigma_scaling()
map_data = fft_map.real_map_unpadded()
# Write real Fourier map into MRC file
iotbx.mrcfile.write_ccp4_map(
  file_name   = "fourier_map.mrc",
  unit_cell   = f_calc.unit_cell(),
  space_group = f_calc.crystal_symmetry().space_group(),
  map_data    = map_data.as_double(),
  labels      = flex.std_string(["Some text"]))
# Calculate exact map and write it down
crystal_gridding = maptbx.crystal_gridding(
  unit_cell        = xrs.unit_cell(),
  space_group_info = xrs.space_group_info(),
  symmetry_flags   = maptbx.use_space_group_symmetry,
  step             = 0.3)
m = mmtbx.real_space.sampled_model_density(
  xray_structure = xrs,
  n_real         = crystal_gridding.n_real())
map_data = m.data()
iotbx.mrcfile.write_ccp4_map(
  file_name   = "exact_map.mrc",
  unit_cell   = f_calc.unit_cell(),
  space_group = f_calc.crystal_symmetry().space_group(),
  map_data    = map_data.as_double(),
  labels      = flex.std_string(["Some text"]))
