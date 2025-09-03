from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from iotbx.map_model_manager import map_model_manager # load map_model_manager
mmm=map_model_manager()  # get initialized instance of the map_model_manager
mmm.generate_map() # get a model and calculate a map for it
map_data = mmm.map_data()  #  our 3D map object
lower_bounds = (10,10,10)  # lower bounds for boxed map
upper_bounds = (21,31,21)  # upper bounds for boxed map
from cctbx import maptbx            # import maptbx
box_map_data = maptbx.copy(map_data, lower_bounds, upper_bounds) # box the map
print( box_map_data.origin())  # prints (10, 10, 10)
print( box_map_data.all())     # prints (12, 22, 12)
print( box_map_data.last(False)) # prints (21, 31, 21)
print( box_map_data[11,12,13])  # prints 0.0416163499881
print( box_map_data.size() )  # prints 3168
shifted_box_map_data = box_map_data.shift_origin()   # shift origin to (0,0,0)
print(shifted_box_map_data.origin())  # prints (0, 0, 0)
print(shifted_box_map_data.all())     # prints (12, 22, 12)
print(shifted_box_map_data.last(False)) # prints (11, 21, 11)
print(shifted_box_map_data[1,2,3])  # prints 0.0416163499881
boxed_mmm = mmm.extract_all_maps_with_bounds( # create box
   lower_bounds = lower_bounds,  # lower bounds
   upper_bounds = upper_bounds)  # upper bounds
new_shifted_box_map_data = boxed_mmm.map_manager().map_data() #
print(new_shifted_box_map_data.origin())  # prints (0, 0, 0)
print(new_shifted_box_map_data.all())     # prints (12, 22, 12)
print(new_shifted_box_map_data.last(False)) # prints (11, 21, 11)
print(new_shifted_box_map_data[1,2,3])  # prints 0.0416163499881
boxed_mmm.write_map('boxed_map.ccp4')  # superimposes on orig
working_sites_cart = boxed_mmm.model().get_sites_cart() # sites
boxed_mmm = mmm.extract_all_maps_with_bounds( # create box
   lower_bounds = lower_bounds,  # lower bounds
   upper_bounds = upper_bounds)  # upper bounds
print (mmm.model().get_sites_cart()[0])  # 14.476000000000003, 10.57, 8.342)
print (mmm.map_manager().map_data()[11,12,13]) # prints 0.0416163499881
print(boxed_mmm.model().get_sites_cart()[0])# (7.005666666666668, 3.339250000000002, 0.967625000000001)
print (boxed_mmm.map_manager().map_data()[1,2,3]) # prints 0.0416163499881
boxed_sites_cart = boxed_mmm.model().get_sites_cart() # get boxed sites
boxed_sites_cart[0] = (10,10,10) # set value of one coordinate in boxed sites
boxed_mmm.model().set_sites_cart(boxed_sites_cart) # set coordinates in model
boxed_mmm.map_manager().map_data()[1,2,3] = 77.  # change map value
print (mmm.model().get_sites_cart()[0])  # 14.476000000000003, 10.57, 8.342)
print (mmm.map_manager().map_data()[11,12,13]) # prints 0.0416163499881
mmm_model_ref = mmm.model()  # reference to model in mmm
mmm_map_manager_ref = mmm.map_manager()  # reference to model in mmm
mmm.box_all_maps_with_bounds_and_shift_origin( # change mmm in place
   lower_bounds = lower_bounds,  # lower bounds
   upper_bounds = upper_bounds)  # upper bounds
print (mmm.model().get_sites_cart()[0]) # (7.005666666666668, 3.339250000000002, 0.967625000000001)
print (mmm.map_manager().map_data()[1,2,3]) # prints 0.0416163499881
sites_cart = mmm.model().get_sites_cart() # get boxed sites
sites_cart[0] = (20,20,20) # set value of one coordinate  in sites_cart
mmm.model().set_sites_cart(sites_cart) # set coordinates in model
mmm.map_manager().map_data()[1,2,3] = 222.  # change map value
print (mmm_model_ref.get_sites_cart()[0])  # (20.0, 20.000000000000004, 20.0)
print (mmm_map_manager_ref.map_data()[11,12,13]) # prints 0.0416163499881
m = boxed_mmm.model()  # get the model
print(m)   # prints info about the model including origin shift
shift_cart = m.shift_cart()  # current origin shift
shift_to_apply = tuple([-x for x in shift_cart])  # opposite shift (to apply()
m.shift_model_and_set_crystal_symmetry(shift_to_apply)  # shift the model
print(m)  # now the origin shift is zero (original location)
boxed_mmm.add_model_by_id(model_id = 'model', model = m)  # load the model in
print(m)  #  automatically shifted to match the map_model_manager origin
m.shift_model_and_set_crystal_symmetry(shift_to_apply)  # shift the model again
print(m)  # now the origin shift is zero (original location)
boxed_mmm.shift_any_model_to_match(m)  # shift this model to match the map_model_manager
print(m)  #  automatically shifted to match the map_model_manager origin
mm = boxed_mmm.map_manager()  # get a map manager
mm.set_model_symmetries_and_shift_cart_to_match_map(m)  # set the symmetry and origin
