from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import absolute_import, division, print_function
import sys
import mmtbx.secondary_structure
from scitbx.array_family import flex
from libtbx.utils import null_out
from iotbx.data_manager import DataManager

def match_score(x,y):
  assert x.size() == y.size()
  match_cntr = 0
  for x_,y_ in zip(x,y):
    if(x_==y_): match_cntr+=1
  return match_cntr/x.size()

def get_ss(hierarchy,
           sec_str_from_pdb_file=None,
           method="ksdssp",
           use_recs=False):
  if(use_recs): params = None
  else:
    params = mmtbx.secondary_structure.manager.get_default_ss_params()
    params.secondary_structure.protein.search_method=method
    params = params.secondary_structure
  ssm = mmtbx.secondary_structure.manager(
    pdb_hierarchy         = hierarchy,
    sec_str_from_pdb_file = sec_str_from_pdb_file,
    params                = params,
    log                   = null_out())
  alpha = ssm.helix_selection()
  beta  = ssm.beta_selection()
  assert alpha.size() == beta.size() == hierarchy.atoms().size()
  annotation_vector = flex.double(hierarchy.atoms().size(), 0)
  annotation_vector.set_selected(alpha, 1)
  annotation_vector.set_selected(beta, 2)
  return annotation_vector

def run(args):
  dm = DataManager()                    #   Initialize the DataManager and call it dm
  dm.set_overwrite(True)                #   tell the DataManager to overwrite files with the same name
  model_filename = args[0]              #   Name of model file
  model = dm.get_model(model_filename)  #   Deliver model object with model info
  pdb_hierarchy = model.get_hierarchy() #   Get hierarchy object
  sec_str_from_pdb_file = model.get_ss_annotation()
  # get secodary structure annotation vector from HELIX/SHEET records (file header)
  print('Running secondary structure annotation...')
  v1 = get_ss(
    hierarchy             = pdb_hierarchy,
    sec_str_from_pdb_file = sec_str_from_pdb_file)
  # get secodary structure annotation vector from method CA atoms
  v2 = get_ss(hierarchy = pdb_hierarchy, method = "from_ca")
  # secodary structure annotation vector from KSDSSP
  v3 = get_ss(hierarchy = pdb_hierarchy, method = "ksdssp")
  #
  print()
  print("CC REMARK vs from_ca:", flex.linear_correlation(x = v1, y = v2).coefficient())
  print("CC REMARK vs ksdssp:", flex.linear_correlation(x = v1, y = v3).coefficient())
  print("CC from_ca vs ksdssp:", flex.linear_correlation(x = v3, y = v2).coefficient())
  print()
  print("match REMARK vs from_ca:", match_score(x = v1, y = v2))
  print("match REMARK vs ksdssp:", match_score(x = v1, y = v3))
  print("match from_ca vs ksdssp:", match_score(x = v3, y = v2))

if __name__ == '__main__':
  run(args=sys.argv[1:])
