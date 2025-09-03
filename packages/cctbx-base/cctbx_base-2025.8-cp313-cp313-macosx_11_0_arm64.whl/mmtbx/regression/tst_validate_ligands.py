from __future__ import absolute_import, division, print_function
import time, os
from libtbx.utils import null_out
import libtbx.load_env
from libtbx.test_utils import approx_equal
from iotbx.cli_parser import run_program
from mmtbx.programs import validate_ligands as val_lig

# ------------------------------------------------------------------------------

def run():
  run_test1()
  os.remove('one_chain_ligand_water_newH.cif')
  os.remove('one_chain_ligand_water_newH.txt')
  run_test2()
  os.remove('two_chains_ligand_water_newH.cif')
  os.remove('two_chains_ligand_water_newH.txt')
  run_test3()
  os.remove('pdb1avd.ent_newH.txt')
  os.remove('pdb1avd.ent_newH.cif')

# ------------------------------------------------------------------------------

def run_test1():
  '''
  Test if iselection for ligand PG5 (chain A resseq 201) is correct.
  '''
  pdb_fname = libtbx.env.find_in_repositories(
    relative_path="mmtbx/regression/pdbs/one_chain_ligand_water.pdb",
    test=os.path.isfile)
  args=[pdb_fname]
  print("mmtbx.development.validate_ligands %s" %(" ".join(args)))
  try:
    result = run_program(program_class=val_lig.Program,args=args,
     logger = null_out())
  except Exception as e:
    msg = traceback.format_exc()

  vl_manager = result.ligand_manager

  assert (len(vl_manager) == 1)
  for lr in vl_manager:
    assert (lr.id_str == 'PG5 A 201')
  # test iselection
  assert(list(lr.ligand_isel) == [190, 191, 192, 193, 194, 195, 196, 197, 198, 199,
    200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214,
    215, 216, 217, 218, 219])


#  tst_get_overlaps(vl_manager = vl_manager)
# or
  for lr in vl_manager:
    clashes_result = lr.get_overlaps()
    assert(clashes_result.n_clashes == 5)
    #print(round(clashes_result.clashscore,1), 27.6)
    assert approx_equal(clashes_result.clashscore, 27.6, eps=0.5)

# ------------------------------------------------------------------------------

def run_test2():
  '''
  Test
  - occupancy determination for ligands
  - adp determination for ligands and neighbors
  '''
  pdb_fname = libtbx.env.find_in_repositories(
    relative_path="mmtbx/regression/pdbs/two_chains_ligand_water.pdb",
    test=os.path.isfile)
  args=[pdb_fname]
  print("mmtbx.development.validate_ligands %s" %(" ".join(args)))
  try:
    result = run_program(program_class=val_lig.Program,args=args,
     logger = null_out())
  except Exception as e:
    msg = traceback.format_exc()

  vl_manager = result.ligand_manager
  tst_occupancies(vl_manager = vl_manager)
  tst_adps(vl_manager = vl_manager)

# ------------------------------------------------------------------------------

def tst_occupancies(vl_manager):
  '''
  Test occupancies
  '''
  assert (len(vl_manager) == 5)
  for lr in vl_manager:
    occs = lr.get_occupancies()
    id_str = lr.id_str
    if (id_str.strip() == 'ABEN A   2'):
      assert approx_equal(occs.occ_mean, 0.56, eps=0.01)
    if (id_str.strip() == 'BBEN A   2'):
      assert approx_equal(occs.occ_mean, 0.44, eps=0.01)
    if (id_str.strip() == 'SO4 A   3'):
      assert approx_equal(occs.occ_mean, 0.65, eps=0.01)
    if (id_str.strip() == 'SO4 A   4'):
      assert approx_equal(occs.occ_mean, 0.48, eps=0.01)
    if (id_str.strip() == 'GOL A   5'):
      assert approx_equal(occs.occ_mean, 0.67, eps=0.01)

# ------------------------------------------------------------------------------

def tst_adps(vl_manager):
  '''
  Test ADPs of ligands and surrounding atoms
  '''
  for lr in vl_manager:
    occs = lr.get_occupancies()
    id_str = lr.id_str
    adps = lr.get_adps()
    if (id_str == 'ABEN B   2'):
      assert(adps.n_iso == 0)
      assert(adps.n_aniso == 9)
      assert(adps.b_min_within is None)
      assert approx_equal([adps.b_min, adps.b_max, adps.b_mean],
        [4.7, 8.1, 6.0], eps=0.1)
    if (id_str.strip() == 'BBEN B   2'):
      assert(adps.n_iso == 0)
      assert(adps.n_aniso == 9)
      assert(adps.b_min_within is None)
      assert approx_equal([adps.b_min, adps.b_max, adps.b_mean],
        [5.1, 8.2, 6.4], eps=0.1)
    if (id_str.strip() == 'SO4 B   3'):
      assert(adps.n_iso == 5)
      assert(adps.n_aniso == 0)
      assert(adps.b_min_within is None)
      assert approx_equal([adps.b_min, adps.b_max, adps.b_mean],
        [7.4,13.1,10.2], eps=0.1)
    if (id_str.strip() == 'SO4 B   4'):
      assert(adps.n_iso == 0)
      assert(adps.n_aniso == 5)
      assert(adps.b_min_within is None)
      assert approx_equal([adps.b_min, adps.b_max, adps.b_mean],
        [10.3,14.6,12.3], eps=0.1)
    if (id_str.strip() == 'GOL B   5'):
      assert(adps.n_iso == 6)
      assert(adps.n_aniso == 0)
      assert(adps.b_min_within is None)
      assert approx_equal([adps.b_min, adps.b_max, adps.b_mean],
        [58.7,114.9,96.9], eps=0.1)

# ------------------------------------------------------------------------------

def run_test3():
  '''
  Test
  - CC calculation for three ligands
  - ADP calculations for ligands
  - occupancy calculations for ligands
  '''
  mtz_fname = libtbx.env.find_in_repositories(
    relative_path="phenix_regression/reflection_files/1avd.mtz",
    test=os.path.isfile)
  pdb_fname = libtbx.env.find_in_repositories(
    relative_path="phenix_regression/pdb/pdb1avd.ent.gz",
    test=os.path.isfile)
  args=[pdb_fname, mtz_fname]
  #
  print("mmtbx.development.validate_ligands %s" %(" ".join(args)))
  try:
    result = run_program(program_class=val_lig.Program,args=args,
     logger = null_out())
  except Exception as e:
    msg = traceback.format_exc()

  vl_manager = result.ligand_manager

  for lr in vl_manager:
    occs = lr.get_occupancies()
    id_str = lr.id_str
    adps = lr.get_adps()
    ccs = lr.get_ccs()
    clashes_result = lr.get_overlaps()
    #
    if (id_str.strip() == 'NAG A 600'):
      assert approx_equal(ccs.cc_2fofc, 0.87, eps=0.03)
      #
      assert approx_equal(occs.occ_min, 0, eps=0.01)
      assert approx_equal(occs.occ_max, 1, eps=0.01)
      assert approx_equal(occs.occ_mean, 0.86, eps=0.01)
      #
      assert approx_equal(adps.b_min, 27.99, eps=0.01)
      assert approx_equal(adps.b_max, 90.00, eps=0.01)
      assert approx_equal(adps.b_mean, 70.71, eps=0.05)
      #
      assert approx_equal(adps.b_min_within, 5.23, eps=0.01)
      assert approx_equal(adps.b_max_within, 79.14, eps=0.01)
      assert approx_equal(adps.b_mean_within, 35.37, eps=0.02)
      #
      assert(clashes_result.n_clashes == 1)
      #print(round(clashes_result.clashscore,1))
      assert approx_equal(clashes_result.clashscore, 9.4, eps=0.5)
      #
    if (id_str.strip() == 'BTN A 400'):
      assert approx_equal(ccs.cc_2fofc, 0.94, eps=0.03)
      #
      assert approx_equal(occs.occ_mean, 1, eps=0.01)
      #
      assert approx_equal(adps.b_min, 4.00, eps=0.01)
      assert approx_equal(adps.b_max, 90.00, eps=0.01)
      assert approx_equal(adps.b_mean, 31.19, eps=0.05)

      assert approx_equal(adps.b_min_within, 4.00, eps=0.01)
      assert approx_equal(adps.b_max_within, 54.65, eps=0.01)
      assert approx_equal(adps.b_mean_within, 23.23, eps=0.02)
      #
      assert(clashes_result.n_clashes == 4)
      #print(round(clashes_result.clashscore,1))
      assert approx_equal(clashes_result.clashscore, 13.0, eps=0.5)
      #
    if (id_str.strip() == 'BTN B 401'):
      assert approx_equal(ccs.cc_2fofc, 0.95, eps=0.03)
      #
      assert approx_equal(occs.occ_mean, 1, eps=0.01)
      #
      assert approx_equal(adps.b_min, 4.00, eps=0.01)
      assert approx_equal(adps.b_max, 46.67, eps=0.01)
      assert approx_equal(adps.b_mean, 23.04, eps=0.05)
      #
      assert approx_equal(adps.b_min_within, 4.00, eps=0.01)
      assert approx_equal(adps.b_max_within, 75.42, eps=0.01)
      assert approx_equal(adps.b_mean_within, 28.16, eps=0.02)
      #
      assert(clashes_result.n_clashes == 6)
      #print(round(clashes_result.clashscore,1))
      assert approx_equal(clashes_result.clashscore, 18.5, eps=0.5)

      #print(adps.b_min_within)
      #print(adps.b_max_within)
      #print(adps.b_mean_within)
      #print(occs.occ_min)
      #print(occs.occ_max)
      #print(occs.occ_mean)
      #print(adps.b_min)
      #print(adps.b_max)
      #print(adps.b_mean)

#def tst_get_overlaps(vl_manager):
#  '''
#  Test nonbonded overlaps
#  '''
#  for id_tuple, ligand_dict in vl_manager.items():
#    for altloc, lr in ligand_dict.items():
#      clashes_result = lr.get_overlaps()
#      assert(clashes_result.n_clashes == 5)
#      assert approx_equal(clashes_result.clashscore, 31.6, eps=1.0)
# anaconda
#(['pdb=" HE3 MET A 107 "', 'pdb=" H81 PG5 A 201 "'], 17, 54, 2.0370952358689647, 2.44, '', None),
#(['pdb=" CE  MET A 107 "', 'pdb=" C8  PG5 A 201 "'], 15, 34, 2.946989989803154, 3.4, '', None),
#(['pdb=" CE  MET A 107 "', 'pdb=" H83 PG5 A 201 "'], 15, 56, 2.4839921497460486, 2.92, '', None)
#
# MAC
#(['pdb=" CE  MET A 107 "', 'pdb=" C8  PG5 A 201 "'], 16, 35, 2.946989989803154, 3.4, '', None),
#(['pdb=" HE3 MET A 107 "', 'pdb=" H83 PG5 A 201 "'], 18, 57, 2.026073542594147, 2.44, '', None),
#(['pdb=" CE  MET A 107 "', 'pdb=" H81 PG5 A 201 "'], 16, 55, 2.4973179613337146, 2.92, '', None)
#
# Readyset gives different names to H atoms.

# ------------------------------------------------------------------------------

if (__name__ == "__main__"):
  t0 = time.time()
  run()
  print("OK. Time: %8.3f" % (time.time()-t0))
