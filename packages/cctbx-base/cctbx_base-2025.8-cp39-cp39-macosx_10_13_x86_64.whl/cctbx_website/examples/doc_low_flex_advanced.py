from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from iotbx.map_model_manager import map_model_manager # load map_model_manager
mmm=map_model_manager() # get an initialized instance of the map_model_manager
mmm.generate_map()# get a model from a small library model and calculate a map
map_data = mmm.map_manager().map_data()  # the map as flex.double() 3D array)
acc = map_data.accessor() #  gridding for map_data
acc.show_summary()        # summarize
print(map_data.last()) # prints (30, 40, 32)  corner of unit cell of map
print(map_data.last(False)) # prints (29, 39, 31) corner of available map
print(map_data.size())    # prints 38400 = 30 x 40 x 32
map_data_as_1d = map_data.as_1d()   # 1D view of map_data
print(map_data_as_1d.size())    # prints 38400, same as the original map_data
map_data_as_1d[0] = 100.   # set a value in map_data_as_1d
print (map_data_as_1d[0])  # prints 100.
print (map_data[0,0,0])  # prints 100.
from scitbx.array_family.flex import grid
new_acc = grid((10,0,0), (40,40,32))  # now from (10,0,0) to (40,40,32)
map_data.reshape(new_acc) #  reshape map_data
map_data.accessor().show_summary()  # summarize map_data now
map_data_as_1d = map_data.as_1d()   # 1D view of map_data
map_data_as_1d[27] = 100.   # set a value in map_data_as_1d
print (map_data_as_1d[27])  # prints 100.
map_data_new_origin = map_data.shift_origin()  # shift and make new array
map_data_new_origin_as_1d = map_data_new_origin.as_1d() # 1D view
print (map_data_new_origin_as_1d[27])  # prints 100 again
map_data_as_1d[27] = 200   # set a new value in map_data
print (map_data_new_origin_as_1d[27])  # prints 200
map_data[0] = 200   # set a few values to 200
map_data[27] = 200   # set a few values to 200
map_data[3973] = 200   # set a few values to 200
sel = (map_data > 100)   #  select all map data elements > 100
print (sel.count(True))   # prints 3, the number of True elements
isel = sel.iselection()  # list of indices the elements in sel that are True
print (isel.size())   # prints 3, how many elements are in isel
print (list(isel))   # prints [0, 27, 3973]
map_data.set_selected(sel, 300)  # set selected elements of map_data to 300
