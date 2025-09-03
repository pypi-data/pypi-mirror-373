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
map_file="map.mrc"                             #   Name of map file
mm = dm.get_real_map(map_file)                 #   Deliver map_manager object with map info
model_file="model.pdb"                         #   Name of model file
model = dm.get_model(model_file)               #   Deliver model object with model info
from iotbx.map_model_manager import map_model_manager  # load map_model_manager
mmm = map_model_manager(        # a new map_model_manager
  model = model,                # initializing with a model
  map_manager = mm )            # and a map_manager
mm = mmm.map_manager()       #  get the map_manager, origin at (0,0,0)
model = mmm.model()          #  get the model, origin matching the map_manager
dm.write_real_map_file(mm,filename="my_map_original_location.mrc")    # write map
dm.write_model_file(model,filename="my_model_original_location", format="pdb") # model
box_mmm = mmm.extract_all_maps_around_model(          # extract a box around model
    selection_string="resseq 219:223")                # select residues 219-223 of model
dm.write_real_map_file(box_mmm.map_manager(),         # get the boxed map_manager
     filename="box_around_219-223.mrc")               # write the map out
#
dm.write_model_file(box_mmm.model(),                  # get the boxed model
      filename="box_around_219-223", format="pdb") # write out boxed model
box_mmm = mmm.extract_all_maps_with_bounds(      #  Use specified bounds to cut out box
   lower_bounds=(1,1,1), upper_bounds=(9,6,3))   #  Lower and upper bounds of box
#
box_mmm = mmm.extract_all_maps_around_density(   #  Find the density in the map and box
    box_cushion = 1)                             # make box just 1 A bigger than density
#
box_mmm = mmm.extract_all_maps_around_unique(    # Find unique part of density and box
    resolution = 3, molecular_mass=2300   )      # resolution of map and molecular_mass,
                                                 # sequence, or solvent_content is required
mmm_copy=mmm.deep_copy()                             # work with a copy of mmm
mmm_copy.box_all_maps_with_bounds_and_shift_origin(  #  Use specified bounds to cut out box
   lower_bounds=(1,1,1), upper_bounds=(9,6,3))       #  Lower and upper bounds of box
box_mmm = mmm.extract_all_maps_around_model(          # extract a box around model
    selection_string="resseq 219:223")                # select residues 219-223 of model
box_mmm_dc = box_mmm.deep_copy()     # save a copy of map_manager
box_mmm.create_mask_around_atoms()   #  create binary mask around atoms in box_mmm model
box_mmm.apply_mask_to_maps()   #  apply existing mask to all maps in box_mmm
dm.write_real_map_file(box_mmm_dc.map_manager(),filename="starting_map.mrc") # original
dm.write_real_map_file(box_mmm.map_manager()   ,filename="masked_map.mrc") # masked
box_mmm_soft_mask=box_mmm_dc.deep_copy()                       # make a copy to work with
box_mmm_soft_mask.create_mask_around_atoms(soft_mask = True)   #  create soft mask
box_mmm_soft_mask.apply_mask_to_maps()   #  apply existing mask to all maps
dm.write_real_map_file(box_mmm_soft_mask.map_manager(),     # write out masked map
       filename="soft_masked.mrc")                         # soft masked
