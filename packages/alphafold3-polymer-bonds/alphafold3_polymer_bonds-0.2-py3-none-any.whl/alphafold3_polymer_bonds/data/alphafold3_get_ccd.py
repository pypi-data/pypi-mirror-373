# time singularity exec --bind $(pwd):/app/scripts /cluster/project/beltrao/shared/alphafold3/images/alphafold3_2e2ffc1.sif sh -c 'python /app/scripts/alphafold3_get_ccd.py' > polybonds.cif
# time singularity exec --bind $(pwd):/app/scripts /cluster/project/beltrao/shared/alphafold3/images/alphafold3_2e2ffc1.sif sh -c 'python /app/scripts/alphafold3_get_ccd.py' > polybonds.json
import json, sys
from pprint import pprint

from alphafold3.cpp import cif_dict
from alphafold3.constants import chemical_components
from alphafold3.constants import residue_names
from alphafold3.data.tools import rdkit_utils

from rdkit.Chem.rdchem import RWMol

def eprint(*args, **kwargs): # https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
    print(*args, file=sys.stderr, **kwargs)

ccd = chemical_components.Ccd()

def get_polybonds(component_id, component_id_suffix, leaving_atoms={}):
    ccd_cif = ccd.get(component_id)
    ccd_mol = rdkit_utils.mol_from_ccd_cif(ccd_cif)
    eprint(f'loaded molecule: {component_id}, n_atoms={ccd_mol.GetNumAtoms()}, n_bonds={ccd_mol.GetNumBonds()}')

    user_mol = RWMol(ccd_mol)
    with user_mol as user_mol_:
        for atom in user_mol_.GetAtoms():
            if atom.GetProp('atom_name') in leaving_atoms:
                user_mol_.RemoveAtom(atom.GetIdx())

    eprint(f'edited molecule: {component_id}, n_atoms={user_mol.GetNumAtoms()}, n_bonds={user_mol.GetNumBonds()}')
    missing_keys = {
        '_chem_comp.formula': ccd_cif['_chem_comp.formula'],
        '_chem_comp.formula_weight': ccd_cif['_chem_comp.formula_weight'],
        '_chem_comp.mon_nstd_parent_comp_id': [ component_id ],
        '_chem_comp.name': ccd_cif['_chem_comp.name'],
        '_chem_comp.pdbx_synonyms': ccd_cif['_chem_comp.pdbx_synonyms'],
        '_chem_comp.type': ccd_cif['_chem_comp.type'],
    }
    user_cif = rdkit_utils.mol_to_ccd_cif(user_mol, component_id=f'{component_id}_{component_id_suffix}').copy_and_update(missing_keys)
    return user_cif

user_dict = dict()
#pprint(residue_names.PROTEIN_TYPES + residue_names.NUCLEIC_TYPES)
for component_id in residue_names.PROTEIN_TYPES + residue_names.NUCLEIC_TYPES: # XXX_POLYBONDS - identical copies for 20 standard amino acids
    user_cif = get_polybonds(component_id, 'POLYBONDS')
    user_cif_str = user_cif.to_string()
    #sys.stdout.write(user_cif_str)
    user_dict[component_id] = user_cif_str

#print(json.dumps({'userCCD': user_cif_str}, indent=2))
print(json.dumps(user_dict, indent=2))
