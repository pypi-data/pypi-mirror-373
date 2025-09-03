from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import absolute_import, division, print_function
from mmtbx.secondary_structure.build import ss_idealization as ssb
ph_helix = ssb.secondary_structure_from_sequence(ssb.alpha_helix_str,"ILMKARNDWYV")
ph_helix.write_pdb_file(file_name="m-helix.pdb")
ph_strand = ssb.secondary_structure_from_sequence(ssb.beta_pdb_str,"ILMKARNDWYV")
ph_strand.write_pdb_file(file_name="m-strand.pdb")
