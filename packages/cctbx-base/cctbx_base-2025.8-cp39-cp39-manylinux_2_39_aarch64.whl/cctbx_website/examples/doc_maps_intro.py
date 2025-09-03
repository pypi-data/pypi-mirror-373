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
print(map_data.all())     # prints (30, 40, 32)
print(map_data.size(), 30*40*32)     # prints 38400, 38400
print(map_data.origin())   # prints (0, 0, 0)
print(map_data.last(False))     # prints (29, 39, 31) last available point
print(map_data.last())          # prints (30, 40, 32) start of next unit cell
print(map_data[1,2,3])    # prints -0.0164242834519
site_frac = [i/n for i,n in zip ((11,12,13), map_data.all())] # fractional
print(site_frac) # prints [0.36666666666666664, 0.3, 0.40625]
uc = mmm.crystal_symmetry().unit_cell()  # unit_cell object for our model
site_cart = uc.orthogonalize(site_frac)  # convert to orthogonal Angstroms
print(site_cart) # prints (8.217366666666667, 8.676899999999998, 9.5866875)
site_frac_again = uc.fractionalize(site_cart)  # convert to fractional
print(site_frac_again) # prints ((0.3666666666666667, 0.3, 0.40625)
grid_point =  [n * f for n,f in zip(map_data.all(), site_frac_again)] # grid
print(grid_point) # prints [11.0, 12.0, 13.0]
print(map_data.value_at_closest_grid_point(site_frac)) #  0.0416163499881
print(map_data[11,12,13]) #  0.0416163499881
