from __future__ import division
import os,copy

import annlib_adaptbx
import libtbx.load_env

annlib_under_build = libtbx.env.under_build("annlib_adaptbx")
annlib_adaptbx_dir = os.path.dirname(annlib_adaptbx.__file__)
annlib_under_build_include = os.path.join(annlib_under_build,"include")
annlib_dir = libtbx.env.dist_path("annlib")

def yield_includes(search_mode):
  annlib_mode_include = os.path.join(annlib_under_build_include,
     "ANN"+search_mode.upper())
  if not os.path.isdir(annlib_under_build_include): os.makedirs(annlib_under_build_include)
  if not os.path.isdir(annlib_mode_include): os.makedirs(annlib_mode_include)
  annlib_include = os.path.join(annlib_dir,"include")
  ANN_include = os.path.join(annlib_include,"ANN")
  for item in os.listdir(ANN_include):
    yield {'src':os.path.join(ANN_include,item),
           'dst':os.path.join(annlib_mode_include,item)}

def yield_src_includes(search_mode):
  annlib_mode_src = os.path.join(annlib_under_build,
     search_mode)
  if not os.path.isdir(annlib_mode_src): os.makedirs(annlib_mode_src)
  annlib_src = os.path.join(annlib_dir,"src")
  for item in os.listdir(annlib_src):
    if item.find(".h")>0:
      yield {'src':os.path.join(annlib_src,item),
             'dst':os.path.join(annlib_mode_src,item)}

def yield_src(search_mode):
  annlib_mode_src = os.path.join(annlib_under_build,
     search_mode)
  if not os.path.isdir(annlib_mode_src): os.makedirs(annlib_mode_src)
  annlib_src = os.path.join(annlib_dir,"src")
  for item in os.listdir(annlib_src):
    if item.find(".cpp")>0:
      yield {'src':os.path.join(annlib_src,item),
             'dst':os.path.join(annlib_mode_src,item)}

def process_includes(lines,search_mode):
  # Rule 1.  The header guards should reflect the search_mode
  guard_line_no = 0
  while lines[guard_line_no].find("#ifndef") < 0:
    guard_line_no += 1
  for i in [guard_line_no,guard_line_no+1]:
    lines[i] = lines[i].replace("ANN","ANN"+search_mode.upper())

  # Rule 2.  Include path should reflect search mode instance
  line_no = 0
  while line_no < len(lines):
    if lines[line_no].find("#include")>=0 and \
       lines[line_no].find("ANN/")>=0:
       lines[line_no]=lines[line_no].replace("ANN/","ANN"+search_mode.upper()+"/")
    line_no += 1

  # Rule 3.  Enclose functions in namespace
  # 3a.  Opening of the namespace
  line_no = 0
  last_include = 0
  while line_no < len(lines):
    if lines[line_no].find("#include")>=0:
       last_include = copy.copy(line_no)
    line_no += 1
  lines.insert(last_include+1,"namespace ann"+search_mode+" {\n")

  # 3b.  special case for the file "ANN.h" where opening { is inside if clause
  line_no = 0
  last_include = 0
  while line_no < len(lines):
    if lines[line_no].find("<cvalues>")>=0:
       last_include = copy.copy(line_no)
       break
    line_no += 1
  if last_include>0:
    lines.insert(last_include+1,"namespace ann"+search_mode+" {\n")

  # 3c.  Closing of the namespace
  line_no = 0
  last_endif = 0
  while line_no < len(lines):
    if lines[line_no].find("#endif")>=0:
       last_endif = copy.copy(line_no)
    line_no += 1
  lines.insert(last_endif,"} //namespace ann"+search_mode+"\n")

  # Rule 4.  Define ANN_ALLOW_SELF_MATCH
  line_no = 0
  while line_no < len(lines):
    if lines[line_no].find("ANNbool")>=0 and \
       lines[line_no].find("ANN_ALLOW_SELF_MATCH")>=0:
      bool_result = {"self_include":"ANNtrue","self_exclude":"ANNfalse"}
      if lines[line_no].find(bool_result[search_mode])<0:
        code_result = {"self_include":"const ANNbool ANN_ALLOW_SELF_MATCH = ANNtrue;\n",
                       "self_exclude":"const ANNbool ANN_ALLOW_SELF_MATCH = ANNfalse;\n"}
        lines[line_no]=code_result[search_mode]
      break
    line_no += 1
  return

def process_src_includes(lines,search_mode):
  process_includes(lines,search_mode)
  # Rule 5.  Header guards for priority queues
  guard_line_no = 0
  while lines[guard_line_no].find("#ifndef") < 0:
    guard_line_no += 1
  for i in [guard_line_no,guard_line_no+1]:
    lines[i] = lines[i].replace("PR_Q","ANN"+search_mode.upper()+"_PR_Q")

def process_src(lines,search_mode,unit):
  if unit in ["ANN.cpp","bd_tree.cpp",
              "brute.cpp","kd_tree.cpp","kd_util.cpp","perf.cpp"]:
    # Rule 2.  Include path should reflect search mode instance
    line_no = 0
    while line_no < len(lines):
      if lines[line_no].find("#include")>=0 and \
         lines[line_no].find("ANN/")>=0:
         lines[line_no]=lines[line_no].replace("ANN/","ANN"+search_mode.upper()+"/")
      line_no += 1

  if unit in ["ANN.cpp","kd_fix_rad_search.cpp","kd_pr_search.cpp","kd_search.cpp",
              "kd_split.cpp","kd_tree.cpp","kd_util.cpp","perf.cpp"]:
    # Rule 6. Enclosure within namespace
     # 3a.  Opening of the namespace
    line_no = 0
    last_include = 0
    while line_no < len(lines):
      if lines[line_no].find("#include")>=0:
         last_include = copy.copy(line_no)
      line_no += 1
    lines.insert(last_include+1,"namespace ann"+search_mode+" {\n")

    # 6c.  Closing of the namespace
    lines.append("} //namespace ann"+search_mode+"\n")

  if unit in ["bd_fix_rad_search.cpp","bd_pr_search.cpp","bd_search.cpp",
              "bd_tree.cpp","brute.cpp","kd_dump.cpp",]:
    # Rule 7.  Namespace using clause
    line_no = 0
    last_include = 0
    while line_no < len(lines):
      if lines[line_no].find("#include")>=0:
         last_include = copy.copy(line_no)
      line_no += 1
    lines.insert(last_include+1,"using namespace ann"+search_mode+";\n")
