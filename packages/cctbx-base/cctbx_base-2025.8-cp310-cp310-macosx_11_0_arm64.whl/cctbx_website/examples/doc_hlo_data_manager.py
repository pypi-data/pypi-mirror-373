from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from iotbx.map_model_manager import map_model_manager      #   load in the map_model_manager
mmm=map_model_manager()         #   get an initialized instance of the map_model_manager
mmm.generate_map()              #   get a model from a small library model and calculate a map for it
mmm.write_map("map.mrc")        #   write out a map in ccp4/mrc format
mmm.write_model("model.pdb")    #   write out a model in PDB format
from iotbx.data_manager import DataManager    # Load in the DataManager
dm = DataManager()                            # Initialize the DataManager and call it dm
dm.set_overwrite(True)       # tell the DataManager to overwrite files with the same name
dm_many_functions = DataManager(datatypes = ["model", "real_map",
  "phil", "restraint"])   # DataManager data types
model_filename="model.pdb"                         #   Name of model file
dm.process_model_file(model_filename)              #   Read in data from model file
model = dm.get_model(model_filename)               #   Deliver model object with model info
dm.write_model_file(model,filename="output_model.pdb") # write model to a file
map_filename="map.mrc"                    #   Name of map file
dm.process_real_map_file(map_filename)    #   Read in data from map file
mm = dm.get_real_map(map_filename)        #   Deliver map_manager object with map info
dm.write_real_map_file(mm,filename="output_map") # write map
map_coeffs = mm.map_as_fourier_coefficients(d_min = 3)    # map represented by Fourier coefficients
mtz_dataset = map_coeffs.as_mtz_dataset(column_root_label='FC')    # create an mtz dataset
#  mtz_dataset.add_miller_array(
#                 miller_array      = some_other_array_like_map_coeffs,
#                 column_root_label = column_root_label_other_array)
mtz_object=mtz_dataset.mtz_object()      # extract an object that knows mtz format
dm.write_miller_array_file(mtz_object, filename="map_coeffs.mtz") # write map coeffs as MTZ
array_labels = dm.get_miller_array_labels("map_coeffs.mtz")   # List of labels in map_coeffs.mtz
labels=array_labels[0]    #  select the first (only) label string
labels                    # print out the first label string
dm.get_reflection_file_server(filenames=["map_coeffs.mtz"],      # read reflection data.
     labels=[labels])                       # file names and labels are matching lists
miller_arrays=dm.get_miller_arrays()   # extract selected arrays
map_coeffs=miller_arrays[0]    # select the first array in the list called miller_arrays
