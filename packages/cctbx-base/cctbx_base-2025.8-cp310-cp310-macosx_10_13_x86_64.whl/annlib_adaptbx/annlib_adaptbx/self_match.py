from __future__ import division
from six.moves import range
import math,os
from annlib_ext import AnnAdaptor,AnnAdaptorSelfInclude
from scitbx.array_family import flex

import libtbx.load_env
dist_dir = libtbx.env.dist_path("annlib_adaptbx")
tests = os.path.join(dist_dir,"tests")

def data_from_files():
  data = flex.double()
  query = flex.double()

  i = 0
  with open(os.path.join(tests,"data.txt")) as D:
    for line in D:  # x & y coordinates of reference set
      point = line.strip().split(" ")
      data.append(float(point[0]))
      data.append(float(point[1]))
      if i==1000:break
      i+=1

  return data

def excercise_nearest_neighbor():

  data = data_from_files()

  A = AnnAdaptor(data,2)# construct k-d tree for reference set
  A.query(data)               # find nearest neighbors of query points

  for i in range(len(A.nn)):
    #print "Neighbor of (%7.1f,%7.1f), index %6d distance %4.1f"%(
    #data[2*i],data[2*i+1],A.nn[i],math.sqrt(A.distances[i]))
    assert A.nn[i]!=i

  A = AnnAdaptorSelfInclude(data,2)# construct k-d tree for reference set
  A.query(data)               # find nearest neighbors of query points

  for i in range(len(A.nn)):
    #print "Neighbor of (%7.1f,%7.1f), index %6d distance %4.1f"%(
    #data[2*i],data[2*i+1],A.nn[i],math.sqrt(A.distances[i]))
    assert A.nn[i]==i

def check_memory():
  data = data_from_files()
  for x in range(1000):
    AnnAdaptorSelfInclude(data,2).query(data)

if __name__=="__main__":
  excercise_nearest_neighbor()
  #check_memory()
  print ("OK")
