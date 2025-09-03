from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
b = [1,2,3]  # a list of values
a = b   #  does a get the value of b or is it a pointer
print(a)  # prints out [1,2,3]
print(b)  # prints out [1,2,3]
a[1] = 10  # set value of second element of a
print(a)  # prints out [1,10,3]
print(b)  # prints out [1,10,3]
d = list(b)   #   make a new list from b
print (d)  # d looks like b: [1, 10, 3]
b[0] = 20  # set value of first element of b
print(d)  #  d is not a pointer to b: still prints [1, 10, 3]
f = [6,7,8]  #  f is an object (a list)
x = [1,2,f]  # x is a list with some numeric values and an object (f)
print(x)  #  looks like [1, 2, [6, 7, 8]]
y = list(x)   #  make a new list and call it y
print(y)  #  looks like [1, 2, [6, 7, 8]]
x[0]=7  # replace element 0 of x
x[2]=[3,4,5]  # replace element 2 of x
print(y)  #  y is still [1, 2, [6, 7, 8]]
f = [6,7,8]  #  f is an object (a list)
x = [1,2,f]  # a list with some numeric values and an object (f)
y = list(x)   #  make a new list and call it y
print(y)    # looks like [1, 2, [6, 7, 8]]
x[0] = 100   # change element 0 of x
print(x)    # changed:[100, 2, [6, 7, 8]]
print(y)    # still looks like [1, 2, [6, 7, 8]]
f[0] = 32    # change the object f
print(x)    # changed in x:[100, 2, [32, 7, 8]]
print(y)    # the object f within y changes [1, 2, [32, 7, 8]]
from iotbx.map_model_manager import map_model_manager # load map_model_manager
mmm=map_model_manager() # get an initialized instance of the map_model_manager
mmm.generate_map()# get a model from a small library model and calculate a map
map_data = mmm.map_manager().map_data()  # the map as flex.double() 3D array)
map_data_copy = map_data   #  just a pointer to map_data
map_data_deep_copy = map_data.deep_copy()   #  totally new array
from copy import deepcopy  # import deepcopy
map_data_deepcopy = deepcopy(map_data)   #  totally new array
a = [5,3,8]  # a list of numbers
a.sort()  #  sort the list.  Nothing is returned
n = a.count(3)  # count values of 3 and return the number
print(n)  # prints 1
from scitbx.array_family import flex  # import flex
array = flex.double()  # set up a flex.double() array
array.append(100)  # put in a value of 100
array.append(200)  # and a value of 200
print(list(array)) # prints [100.0, 200.0]
sel = (array == 100)  # identify array elements equal to 100
selected_data = array.select(sel)  # returns new object
print(list(selected_data))  # prints [100.0]
print(list(selected_data))  # prints [100.0]
complex_array = flex.complex_double() # a complex double array
complex_array.append((1+2j))   # append the complex number (1+2i)
complex_array.append((23-6j))   # append the complex number (23-6i)
a,b = complex_array.parts()  # pointers a and b to the real and imaginary parts
print(list(complex_array))  # print out the array: [(1+2j), (23-6j)]
print(list(a), list(b))  # prints ([1.0, 23.0], [2.0, -6.0])
a[1] = 99 #  change pointer to a
print(list(complex_array))  # still prints out [(1+2j), (23-6j)]
map_coeffs = mmm.map_manager().map_as_fourier_coefficients()  # map coeffs
print(map_coeffs.data()[0])  # (22.1332152449-33.1246974818j)
data = map_coeffs.data() # the map coefficients themselves
print(data[0]) # the first map coefficient ((22.1332152449-33.1246974818j))
data[0] = (10+6j)  # set value of data[0]
print(map_coeffs.data()[0])  # prints (10+6j)
phases = map_coeffs.phases() # new object with indices and phases only
map_data = mmm.map_manager().map_data()  # 3D flex.double array
map_data_as_1d = map_data.as_1d()  # new object, data are shared
map_data_as_float = map_data.as_float() # new object, new data
print(map_data[0], map_data_as_1d[0], map_data_as_float[0]) #
map_data[0] = 999.  # set map_data
print(map_data[0], map_data_as_1d[0], map_data_as_float[0]) #
from copy import deepcopy  # import deepcopy
x = [1,2,[6,7,8]]  # a list with some values and a list
y = deepcopy(x)   #  completely new copy of x. Change x; nothing happens to y
from iotbx.map_model_manager import map_model_manager # load map_model_manager
mmm=map_model_manager() # get an initialized instance of the map_model_manager
mmm.generate_map()# get a model from a small library model and calculate a map
map_data = mmm.map_manager().map_data()  # the map as flex.double() 3D array)
print(map_data[27])  # prints original value of -0.0131240713008
map_data_pointer = map_data  #  just points to map_data
map_data_deep_copy = map_data.deep_copy()  #  completely new data
map_data[27] = 100  #  set value of map_data
print(map_data_pointer[27])   # prints 100
print(map_data_deep_copy[27])  # prints original value of -0.0131240713008
x = None
if (not x):  # don't use this
  print("""not x can be 0, None, False, "", [], {}, (),...""")   # happens if x is (0, None, False, "", [], {}, (), ...)
if (x is None):  # Use this instead
  print("x is None")   # happens if x is None (only)
if (x is not None):  # Use this too
  print("x is not None")   # happens unless x is None (only)
def my_bad_function(value, current_list = []):   # don't do this
  current_list.append(value)      # current_list from previous call
  return current_list   # returns current_list
print(my_bad_function(1))   #  prints [1]...current_list was []
print(my_bad_function(2))   #  prints [1, 2] ...current_list was [1]
def better_function(value, current_list = None):   # ok way
  if current_list is None:   # catch uninitialized current_list
     current_list = []       # set its value to []
  current_list.append(value)      # works
  return current_list   # returns current_list
print(better_function(1))   #  prints [1]...current_list was []
print(better_function(2))   #  prints [2]...current_list was []
