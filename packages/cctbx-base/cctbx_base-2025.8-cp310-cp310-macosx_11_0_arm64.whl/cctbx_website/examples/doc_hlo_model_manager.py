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
from iotbx.data_manager import DataManager    #   Load in the DataManager
dm = DataManager()                            #   Initialize the DataManager and call it dm
dm.set_overwrite(True)         #   tell the DataManager to overwrite files with the same name
model_filename="model.pdb"                         #   Name of model file
model = dm.get_model(model_filename)               #   Deliver model object with model info
sites_cart = model.get_sites_cart()          #      get coordinates of atoms in Angstroms
print (sites_cart[0])     #    coordinates of first atom
sites_cart = model.get_sites_cart()          # get coordinates of our model
from scitbx.matrix import col                # import a tool that handles vectors
sites_cart += col((1,0,0))                   # shift all coordinates by +1 A in X
model.set_sites_cart(sites_cart)             # replace coordinates with new ones
print (model.get_sites_cart()[0])            # print coordinate of first atom
dm.write_model_file(model, "shifted_model.pdb", overwrite=True)
model_filename="model.pdb"                         #   Name of model file
model = dm.get_model(model_filename)               #   Deliver model object with model info
sel =  model.selection("name CA")     # identify all the atoms in model with name CA
ca_only_model = model.select(sel)     #  select atoms identified by sel and put in new model
print (ca_only_model.as_pdb_or_mmcif_string())      #  print out the CA-only model in PDB format
dm.write_model_file(ca_only_model, "ca_model.pdb", overwrite=True)
model_filename="model.pdb"                         #   Name of model file
model = dm.get_model(model_filename)               #   Deliver model object with model info
from cctbx.development.create_models_or_maps import generate_map_coefficients   # import the tool

map_coeffs = generate_map_coefficients(  # generate map coeffs from model
      model=model,                       # Required model
      d_min=3,                           # Specify resolution
      scattering_table='electron')       # Specify scattering table
from cctbx.development.create_models_or_maps import get_map_from_map_coeffs   #  import the tool
map_data = get_map_from_map_coeffs(map_coeffs = map_coeffs)   #  create map from map coeffs
# mm_model_map= mm.fourier_coefficients_as_map_manager(map_coeffs)   # generate map from map coeffs
