from __future__ import absolute_import, division, print_function
import os
from annlib_adaptbx.source_generators import generate_all

if self.env.is_ready_for_build():
  print('  Generating C++ files for self-inclusive approximate nearest neighbour')
  for search_mode in ["self_include"]:
    for item in generate_all.yield_includes(search_mode):
      #print item
      with open(item['src'],'r') as G:
        lines = G.readlines()
      generate_all.process_includes(lines,search_mode)
      with open(item['dst'],'w') as F:
        F.write(''.join(lines))

    for item in generate_all.yield_src_includes(search_mode):
      #print item
      with open(item['src'],'r') as G:
        lines = G.readlines()
      generate_all.process_src_includes(lines,search_mode)
      with open(item['dst'],'w') as F:
        F.write(''.join(lines))

    for item in generate_all.yield_src(search_mode):
      #print item
      with open(item['src'],'r') as G:
        lines = G.readlines()
      generate_all.process_src(lines,search_mode,os.path.basename(item['src']))
      with open(item['dst'],'w') as F:
        F.write(''.join(lines))
