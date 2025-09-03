from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import print_function  # so we can use print function easily
import sys        # import sys
from libtbx import group_args #  group_args function we will use to return items
def run_something(value):  # simple function
  return value * 2    # just returns 2 * the input value
iteration_list = [5,7,9]  # list of anything
def run_one_by_one(iteration_list): #
  result_list = []                             # initialize result list
  for i in range(len(iteration_list)):         # iterate over input values
    result = run_something(iteration_list[i])  # get result
    result_list.append(result)  # save result
  return result_list   # return the list of results
result_list = run_one_by_one(iteration_list)  # get results one by one
print(result_list)  # prints list of values  [10, 14, 18]
def run_in_parallel(iteration_list, nproc = 4): #
  from libtbx.easy_mp import simple_parallel  # import the simple_parallel code
  result_list = simple_parallel(      # run in parallel
    iteration_list = iteration_list,  # our list of values to run with
    function = run_something,         # the method we are running
    nproc = nproc )                   # how many processors
  return result_list   # return the list of results
result_list = run_in_parallel(iteration_list, nproc = 4)  # run in parallel
print(result_list)  # prints list of values  [10, 14, 18]
def run_advanced(info, big_object = None,  #
     log = sys.stdout):   #  we can specify the log in this method if we want
  output_value = info.value * 2 + big_object[info.index]   # our result
  print("Value: %s Index: %s Output value: %s" %(info.value, info.index, output_value), file = log)
  return group_args( #
    group_args_type = 'Result from one job',  #
    input_info = info,   #
    output_value = output_value,)   #
iteration_list = []   # initialize
from libtbx import group_args
for i in [5,7,9]:  # our values to vary for each job
  iteration_list.append(   # a list of info objects
    group_args(   # info object (group_args)
      group_args_type = 'value of info for one job',   # title
      value = i,   # value of value
      index = 2)   # value of index
    )   #

big_object = [0,1,2,3]  # just some supposedly big object
def advanced_run_as_is(iteration_list,  #
     big_object = None,  #
     log = sys.stdout): # run in usual way
  result_list = []   # initialize
  for i in range(len(iteration_list)):     #  iterate through jobs
    result = run_advanced(iteration_list[i],
      big_object = big_object,
      log = log)  # run job
    result_list.append(result)   #
  return result_list    # return list of results
result_list = advanced_run_as_is( #
   iteration_list, big_object = big_object,
   log = sys.stdout) #
for result in result_list:  # run through results
  print("\nOne result:\n%s" %str(result))  # print this result (it is a group_args object)
def advanced_run_in_parallel(iteration_list,  #
      big_object = None, nproc = 4, log = sys.stdout): # run in parallel w
  from libtbx.easy_mp import simple_parallel  #
  result_list = simple_parallel(  #
    iteration_list = iteration_list, # list of varying inputs
    big_object = big_object, # any number of keyword arguments allowed
    function = run_advanced,  # function to run
    nproc = 3,   # number of processors
    verbose = False,   # non-verbose output
    log = log,
    )
  return result_list
result_list = advanced_run_in_parallel(  #
    iteration_list, #
    big_object = big_object,  #
    log = sys.stdout) #
for result in result_list:  # run through results
  print("\nOne result:\n%s" %str(result))  # print this result (it is a group_args object)
