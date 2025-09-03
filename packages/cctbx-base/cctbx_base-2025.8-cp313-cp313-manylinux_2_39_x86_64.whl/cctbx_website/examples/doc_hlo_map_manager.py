from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from iotbx.data_manager import DataManager     # load in DataManager
dm = DataManager()                             # Get an initialized version as dm
dm.set_overwrite(True)       #   tell the DataManager to overwrite files with the same name
from iotbx.map_model_manager import map_model_manager      #   load in the map_model_manager
mmm=map_model_manager()         #   get an initialized instance of the map_model_manager
mmm.generate_map()              #   get a model from a small library model and calculate a map for it
mmm.write_map("map.mrc")        #   write out a map in ccp4/mrc format
mmm.write_model("model.pdb")    #   write out a model in PDB format
map_filename="map.mrc"                       #   Name of map file
mm = dm.get_real_map(map_filename)           #   Deliver map_manager object with map info
mm.shift_origin()     #  Make sure that the origin is shifted to (0,0,0)
mm.show_summary()
map_data = mm.map_data()    # get the data.
crystal_symmetry=mm.crystal_symmetry()    # get crystal_symmetry
crystal_symmetry    # crystal_symmetry summary
# help(mm)
# help(mm.map_as_fourier_coefficients)
map_data=mm.map_data()    # get map_data. Note this is just a pointer to the map_data
new_map_data  = 2.* map_data    # multiply map_data  times 2 and create new array new_map_data with new values
map_data[3,4,5], new_map_data[3,4,5]
new_mm=mm.customized_copy(map_data=new_map_data)    #  new map_manager with data from new_map_data
dm.write_real_map_file(new_mm,filename="doubled_map.mrc", overwrite=True)    # write map
a=map_data    # get map data
b=new_map_data    # get other map data
c=a*b    # multiply the maps
d=a+b    # add the maps
e=a/b    # divide the maps (without additionael checks, this will crash if any element is zero)
mm_c=mm.customized_copy(map_data=c)    #  new map_manager with data from map c
dm.write_real_map_file(mm_c,filename="a_times_b.mrc", overwrite=True) # write map
value = map_data[4,5,6]  # notice the brackets for specifying indices in a map
map_data_1d = map_data.as_1d()   #    1D view, note that these contain the same data
map_data_1d.size()  # get how many points there are
map_data.size()   # how many points in the original array (the same)
map_data.count(0)  # how many points have a value of zero
map_data_1d.standard_deviation_of_the_sample()  #  standard deviation of data in map_data
sel = ( map_data < 0 )   # select all grid points with values less than zero and call the selection sel
map_data.set_selected(sel, 0)   # set all the points specified by selection sel to zero
map_data.count(0)  # how many points now  have a value of zero
map_file="map.mrc"                             #   Name of map file
mm = dm.get_real_map(map_file)                 #   Deliver map_manager object with map info
map_data = mm.map_data() #  the map as a 3D real-space map
map_coeffs = mm.map_as_fourier_coefficients(  # map represented by Fourier coefficients
     d_min = 3)
map_coeffs.size()               # number of Fourier coefficients in map_coeffs
map_coeffs.d_min()              #  high_resolution limit of map_coeffs
map_coeffs.crystal_symmetry()   # symmetry and cell dimensions of real-space map
indices = map_coeffs.indices()     # indices of each term in the map_coeffs array
data = map_coeffs.data()           #  data (complex numbers) for each index
indices[1], data[1]                # indices and data for first term
map_coeffs_low_res = map_coeffs.resolution_filter(d_min=4)   #  cut resolution to 4 A
map_coeffs_low_res.size()   # number of data in the low_res Fourier representation
mtz_dataset = map_coeffs_low_res.as_mtz_dataset(column_root_label='F')    # mtz dataset
mtz_object=mtz_dataset.mtz_object()            #  extract an object that knows mtz format
dm.write_miller_array_file(mtz_object, filename="map_coeffs_low_res.mtz") #write map coeffs
mm_low_res = mm.fourier_coefficients_as_map_manager(    # convert to real space
     map_coeffs=map_coeffs_low_res)
dm.write_real_map_file(mm_low_res,filename="map_low_res.mrc", overwrite=True) # write map
map_file="map.mrc"                             #   Name of map file
mm = dm.get_real_map(map_file)                #   Deliver map_manager object with map info
mm.set_original_origin_and_gridding(
   original_origin =(100,100,100),              # Set the origin of the part of map we have
   gridding=(200,200,200) )                     # set the gridding of the full map
mm.show_summary()   # summarize.  Full map is (0,0,0) to (200,200,200)
                    # available map is just part of full map
mm.write_map("non_zero_origin_map.ccp4")    # write the map
map_file="non_zero_origin_map.ccp4"                             #   Name of map file
new_mm = dm.get_real_map(map_file)           #   Deliver map_manager object with map info
new_mm.show_summary()    # summarize
new_mm.shift_origin()    # shift the origin to (0,0,0)
shifted_map_data=new_mm.map_data()    # get data to work with, origin at (0,0,0)
dm.write_real_map_file(new_mm,filename="map_after_shifting.mrc") # write map
mm.find_map_symmetry()    # Find symmetry in the map
print ( mm.ncs_object())
from iotbx.regression.ncs.tst_ncs import pdb_str_9 as dimer_text
dm = DataManager(['model'])
model_file = 'model_with_ncs.pdb'
dm.process_model_str(model_file, dimer_text)
m = dm.get_model(model_file)
dm.write_model_file(m, model_file, overwrite=True)
ncs_mmm=map_model_manager()
ncs_mmm.generate_map(box_cushion=0, file_name=model_file)
ncs_map_manager = ncs_mmm.map_manager()
ncs_map_manager.find_map_symmetry()    # Find symmetry in the map
print ( ncs_map_manager.ncs_object())
text = ncs_map_manager.ncs_object().display_all()
