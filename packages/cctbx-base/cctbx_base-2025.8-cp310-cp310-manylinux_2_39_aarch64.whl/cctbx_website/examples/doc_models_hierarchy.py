from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import absolute_import, division, print_function
from iotbx.data_manager import DataManager
import sys
dm = DataManager()                    #   Initialize the DataManager and call it dm
dm.set_overwrite(True)                #   tell the DataManager to overwrite files with the same name
model_filename = sys.argv[1:][0]      #   Name of model file
model = dm.get_model(model_filename)  #   Deliver model object with model info

m = model.deep_copy()                 # work on a copy of model object

pdb_hierarchy = m.get_hierarchy()     #   Get hierarchy object
for chain in pdb_hierarchy.only_model().chains():
  for residue_group in chain.residue_groups():
    for atom_group in residue_group.atom_groups():
      for atom in atom_group.atoms():
        if (atom.element.strip().upper() == "ZN"):
          atom_group.remove_atom(atom)
      if (atom_group.atoms_size() == 0):
        residue_group.remove_atom_group(atom_group)
    if (residue_group.atom_groups_size() == 0):
      chain.remove_residue_group(residue_group)
model_file_name = dm.write_model_file(m, "model_Zn_free.pdb")
print("File name written: %s" %(model_file_name))
pdb_hierarchy = model.get_hierarchy() #   Get hierarchy object
import iotbx.pdb
pdb_hierarchy = iotbx.pdb.input(file_name=model_filename).construct_hierarchy()
sel_cache = pdb_hierarchy.atom_selection_cache()
non_zn_sel = sel_cache.selection("not (resname ZN)")
hierarchy_new = pdb_hierarchy.select(non_zn_sel)
# etc
non_zn_sel= model.selection("not (resname ZN)")
hierarchy_new = model.select(non_zn_sel).get_hierarchy()
m = model.deep_copy()
pdb_hierarchy = m.get_hierarchy()
pdb_atoms = pdb_hierarchy.atoms()
xray_structure = m.get_xray_structure()
sel_cache = pdb_hierarchy.atom_selection_cache()
c_alpha_sel = sel_cache.selection("name ca") # XXX not case sensitive!
c_alpha_atoms = pdb_atoms.select(c_alpha_sel)
c_alpha_xray_structure = xray_structure.select(c_alpha_sel)
c_alpha_hierarchy = pdb_hierarchy.select(c_alpha_sel)
m = model.deep_copy()
pdb_hierarchy = m.get_hierarchy()
for chain in pdb_hierarchy.only_model().chains():
  chain_atoms = chain.atoms()
  chain_selection = chain_atoms.extract_i_seq()
selection = pdb_hierarchy.atom_selection_cache().selection("hetatm")
for chain in pdb_hierarchy.only_model().chains():
  for residue_group in chain.residue_groups():
    residue_isel = residue_group.atoms().extract_i_seq()
    if (selection.select(residue_isel).all_eq(True)):
      #do_something_with_heteroatom_residue(residue_group)
      pass
pdb_hierarchy.reset_atom_i_seqs()
pdb_atoms = pdb_hierarchy.atoms()
pdb_atoms.reset_i_seq()
