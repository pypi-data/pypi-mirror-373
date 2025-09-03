from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
a = (1,2,3)  # a tuple of values
b = (6,6,6) # another tuple of the same length
from scitbx.matrix import col  # import the col methods
c = col(a) + col(b)  #  col objects of the same length can be added together
d = tuple(c)  # now d is a tuple again
print(d)   #  now we get (7,8,9)
from scitbx.array_family import flex # import the flex methods
a = flex.double((1,2,3))  # make a flex array
print(a)  # print it  # you get something like 
print(tuple(a))  # now you can see what is in it: (1.0, 2.0, 3.0)
from scitbx.matrix import col  # import the col methods
a = (1,2,3)   # a tuple
b = (5,3,9)   #  another tuple
d = col(a).dot(col(b))  # dot product of a and b
print(d)     # dot product is 38
from scitbx.matrix import col  # import the col methods
a = (1,2,3)  # a tuple
b = (5,3,9)  # another tuple
ca = col(a)  # col object based on a
cb = col(b)  # col object based on b
print( ca.dot(cb))  # dot product = 38
print( tuple(ca.cross(cb)))  # cross product = (9, 6, -7)
complex_array = flex.complex_double() # a complex double array
complex_array.append((1+2j))   # append the complex number (1+2i)
complex_array.append((23-6j))   # append the complex number (23-6i)
a,b = complex_array.parts()  # pointers a and b to the real and imaginary parts
print(list(complex_array))  # print out the array: [(1+2j), (23-6j)]
print(list(a), list(b))  # prints ([1.0, 23.0], [2.0, -6.0])
from iotbx.map_model_manager import map_model_manager # load map_model_manager
mmm=map_model_manager() # get an initialized instance of the map_model_manager
mmm.generate_map()# get a model from a small library model and calculate a map
map_coeffs = mmm.map_manager().map_as_fourier_coefficients() # get map coeffs
complex_double_array = flex.complex_double()  # a complex double array
indices = map_coeffs.indices()  #  array of indices
sites_cart = mmm.model().get_sites_cart()  # coordinates
def return_a_and_b(a,b): # simple function
  return a,b   # just return a couple values
def return_a_and_b(a,b): # simple function
  from libtbx import group_args   #  import group_args
  result = group_args(              #
    group_args_type = 'just returning a and b',  # a name for this group_args
    a = a,   #   can refer to a as result.a
    b = b)   #   and to b as result.b
  return result  #
result = return_a_and_b(1,2)   # call our function
print(result)   # prints out value of a and b and the label
print(result.a)   # print out value of a
def furthest(sites_cart):  # furthest from center
  center = sites_cart.mean()   # flex method to get mean of vec3_double() array
  diffs = sites_cart - center  # subtract a vector from a vec3_double() array
  norms = diffs.norms()        # get an array of lengths of the diffs array
  return norms.min_max_mean().max  # get maximum value

print(furthest(sites_cart))  # print the result
from scitbx.array_family import flex # import the flex methods
a = flex.vec3_double(((1,1,1),(2,2,2), (3,3,3)))  # make a flex array
b = flex.vec3_double(((3,2,2),(1.1,1.2,1.2),(3,2,2), (4,3,3)))  # make a flex array
dist, i, j = a.min_distance_between_any_pair_with_id(b)  # find closest pair
print(dist, i, j)  # prints  (0.29999999999999993, 0, 1)
a = [5,6,7]  # a list of 3 values
print(a[0])  # prints 5 (indexing starts at zero)
print(a[2])  # prints 7
print(a[-1])  # prints 7
index = -1
index_to_use = len(a) + index   # this is done in the background
print( index, index_to_use, a[index],a[index_to_use]) # prints (-1, 2, 7, 7)
print(a[-3])  # prints 5
a = [5,6,7]  # a list of 3 values
print(a[:2])  # prints [5,6]
print(a[2:])  # prints [7]
k = 2
print(a[:k],a[k:])  # prints ([5, 6], [7])
print( a[k:])  # prints [7]
print( a[k])  # prints 7
print( a[k:k+1])  # prints [7]
print( a[-1:])  # prints [7]
print( a[-1:1])  # prints []
print( a[2:1])  # prints []
from libtbx.test_utils import approx_equal # import it
print( approx_equal(1,1.001))  # prints False (not same within machine precision)
print( approx_equal(1,1.+1.e-50))  # prints True (within machine precision)
print( approx_equal(1,1.001, eps = 0.1)) # prints True (within 0.1)
a=flex.double((1,2,3))  #  set up an array
b = a + 0.0001   # another array that is just a little different
print( approx_equal(a,b) )  #prints False and lists differences
print(  approx_equal(a,b, eps=0.001))  # prints True (all elements within 0.001)
