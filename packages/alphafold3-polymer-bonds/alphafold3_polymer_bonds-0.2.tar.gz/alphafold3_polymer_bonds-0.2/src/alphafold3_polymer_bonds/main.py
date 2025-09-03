#!/usr/bin/env python3
"""
Protein Bond Modeling Script

This script processes AlphaFold3 JSON files to model protein-protein bonds 
using ligand bridges. It identifies bonds between protein chains and modifies 
the structure to represent these bonds through intermediate ligand molecules.

The algorithm works by:
1. Identifying protein-protein bonds from bondedAtomPairs
2. Converting one of the bonded amino acids into a ligand molecule
3. Splitting the original chain and creating new chain segments
4. Establishing bonds through the ligand as an intermediate bridge

This approach allows modeling of complex protein interactions while maintaining
proper chemical connectivity through ligand intermediates.

Usage:
    ./alphafold3_polymer_bonds --source-dir input/ --output-dir output/
    ./alphafold3_polymer_bonds -s input/ -o output/ --verbose

Authors: Ricardo Heinzmann, Jürgen Jänes
"""

import argparse, gzip, importlib, importlib.metadata, importlib.resources, json, string, sys

from copy import deepcopy
from pathlib import Path
from pprint import pprint

from typing import Dict, List, Tuple, Any, TypeAlias
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None #https://github.com/python/typing/issues/182#issuecomment-1320974824

import pandas as pd

import Bio.PDB, Bio.PDB.mmcifio 

poly_to_ligand = {
    'protein': {
        'G': 'GLY', 'A': 'ALA', 'V': 'VAL', 'L': 'LEU', 'I': 'ILE',
        'P': 'PRO', 'F': 'PHE', 'Y': 'TYR', 'W': 'TRP', 'S': 'SER',
        'T': 'THR', 'C': 'CYS', 'M': 'MET', 'N': 'ASN', 'Q': 'GLN',
        'D': 'ASP', 'E': 'GLU', 'K': 'LYS', 'R': 'ARG', 'H': 'HIS'
    },
    'dna': {
        'A': 'DA',
        'G': 'DG',
        'C': 'DC',
        'T': 'DT',
    },
    'rna': {
        'A': 'A',
        'C': 'C',
        'G': 'G',
        'U': 'U',
    },
}

backbone_atoms = {
    'protein': ('C', 'N'),
    'dna': ("C3'", 'OP3'),
    'rna': ("C3'", 'OP3'),
}

def generate_residue_mapping(json_data: JSON) -> pd.DataFrame:
    """
    Generate mapping from input .json with polymer bonds by modelling the second entity in bondedAtomPairs as a ligand.

    Args:
        - json_data AlphaFold3 input with polymer bonds in bondedAtomPairs

    Returns:
        DataFrame wit following columns:
        - id, modified_id
        - pos, modified_pos
        - type, modified_type
    """
    columns_ = ['type', 'id', 'seq']
    df_ = pd.DataFrame.from_records([(next(iter(seq.keys())), next(iter(seq.values()))['id'], next(iter(seq.values()))['sequence']) \
        for seq in json_data['sequences'] if next(iter(seq.keys())) != 'ligand'], columns=columns_)
    df_['seq'] = df_['seq'].map(list)
    df_['pos'] = df_['seq'].map(lambda seq: range(1, len(seq) + 1))

    df_ = df_.explode(['seq', 'pos']).set_index(['id', 'pos'])
    columns_ = ['id1', 'pos1', 'atom1', 'id2', 'pos2', 'atom2']
    bondedAtomPairs_iter = json_data.get('bondedAtomPairs', [])
    bondedAtomPairs = pd.DataFrame.from_records([ 
        (pair_[0][0], pair_[0][1], pair_[0][2], pair_[1][0], pair_[1][1], pair_[1][2]) for pair_ in bondedAtomPairs_iter], columns=columns_)

    df_['modified_type'] = df_['type']
    #df_['modified_ptm'] = False
    for i, r in bondedAtomPairs.iterrows():
        type1 = df_.loc[(r.id1, r.pos1), 'type']
        type2 = df_.loc[(r.id2, r.pos2), 'type']
        print(r.id1, r.pos1, r.id2, r.pos2, type1, type2)
        #if (type1 != 'ligand') and (type2 == 'protein'):
        #    df_.loc[(r.id2, r.pos2), 'modified_ptm'] = True
        if (type1 != 'ligand') and (type2 != 'ligand'):
            df_.loc[(r.id2, r.pos2), 'modified_type'] = 'ligand'

    df_['modified_seq'] = df_['seq']
    for i, r in df_.iterrows():
        if r.type != 'ligand' and r.modified_type == 'ligand':
            df_.loc[i, 'modified_seq'] = poly_to_ligand[r.type][r.seq]

    id_prefix = iter(string.ascii_uppercase)
    df_['modified_id'] = ''
    for (i1, r1), (i2, r2) in zip(df_.iterrows(), df_.iloc[1:].iterrows()):
        if i1[0] != i2[0]: # new chain
            id_prefix = iter(string.ascii_uppercase)
            df_.loc[i2, 'modified_id'] = ''
        elif i1[0] == i2[0] and r1.modified_type != r2.modified_type: # ligand transformation
            df_.loc[i2, 'modified_id'] = next(id_prefix)
        else: # walking along existing chain
            df_.loc[i2, 'modified_id'] = df_.loc[i1, 'modified_id']            
    df_['modified_id'] = df_.index.get_level_values('id') + df_['modified_id']
    df_['modified_pos'] = df_.groupby(['modified_id', 'modified_type']).cumcount() + 1

    cols_ = ['id', 'pos', 'type', 'seq', 'modified_id', 'modified_pos', 'modified_type', 'modified_seq']
    return df_.reset_index()[cols_].set_index(['id', 'pos'])

def generate_modified_json(json_data: JSON, mapping: pd.DataFrame) -> JSON:
    """
    Modify json_data based on the specified residue mapping
    """
    modified_json = deepcopy(json_data)
    # TODO - ordering does not match what's in original file (can infer from json_data)
    sequences = mapping.groupby('modified_id').agg(
        modified_type=('modified_type', lambda x: x.iloc[0]),
        modified_seq=('modified_seq', lambda x: ''.join(x)),
    ).reset_index()

    modified_json['sequences'] = []
    for i, r in sequences.iterrows():
        if r.modified_type == 'ligand':
            modified_json['sequences'].append({
                'ligand': {
                    'id': r.modified_id,
                    'ccdCodes': [ r.modified_seq ],
            }})
        else:
            modified_json['sequences'].append({
            r.modified_type: {
                'id': r.modified_id,
                'sequence': r.modified_seq,
            }})

    for seq in json_data['sequences']:
        if next(iter(seq.keys())) == 'ligand':
            modified_json['sequences'].append(seq)

    def get_(id, pos, col):
        return mapping.loc[(id, pos), col]

    modified_json['bondedAtomPairs'] = []
    for ((id1, pos1, atom1), (id2, pos2, atom2)) in json_data.get('bondedAtomPairs', []):
        type2, modified_type2 = get_(id2, pos2, 'type'), get_(id2, pos2, 'modified_type')
        # If preceding entity exists, add backbone bond
        if (id2, pos2 - 1) in mapping.index and type2 != 'ligand' and modified_type2 == 'ligand':
            modified_json['bondedAtomPairs'].append([
                (get_(id2, pos2 - 1, 'modified_id'), int(get_(id2, pos2 - 1, 'modified_pos')), backbone_atoms[type2][0]),
                (get_(id2, pos2,     'modified_id'), int(get_(id2, pos2,     'modified_pos')), backbone_atoms[type2][1]),
            ])

        # User-specified bond with mapped coordinates 
        modified_json['bondedAtomPairs'].append([
            (get_(id1, pos1, 'modified_id'), int(get_(id1, pos1, 'modified_pos')), atom1),
            (get_(id2, pos2, 'modified_id'), int(get_(id2, pos2, 'modified_pos')), atom2),
        ])

        # If succeeding entity exists, add backbone bond
        if (id2, pos2 + 1) in mapping.index and type2 != 'ligand' and modified_type2 == 'ligand':
            modified_json['bondedAtomPairs'].append([
                (get_(id2, pos2,     'modified_id'), int(get_(id2, pos2,     'modified_pos')), backbone_atoms[type2][0]),
                (get_(id2, pos2 + 1, 'modified_id'), int(get_(id2, pos2 + 1, 'modified_pos')), backbone_atoms[type2][1]),
            ])

    #modified_json['userCCDPath'] = '/cluster/project/beltrao/jjaenes/25.06.03_batch-infer/projects/alphafold3-polymer-bonds/user_ccd/polybonds.cif'
    #userCCD_path = '/cluster/project/beltrao/jjaenes/25.06.03_batch-infer/projects/alphafold3-polymer-bonds/user_ccd/polybonds.json'
    '''
    userCCD_path = importlib.resources.files('alphafold3_polymer_bonds') / 'data/polybonds.json'
    with open(userCCD_path, 'r') as fh:
        userCCD_data = json.load(fh)
        #for lig_ in userCCD_data.values():
        #    print(lig_)
        lig_all_ = ''.join([lig_ for lig_ in userCCD_data.values()])
        modified_json['userCCD'] = lig_all_
        #modified_json['userCCD'] = userCCD_data['userCCD']
    '''
    return modified_json

def post_process_structure(model_path: Path, corrected_model_path: Path, mapping: pd.DataFrame):
    parser = Bio.PDB.MMCIFParser()
    with gzip.open(model_path, 'rt') as fh:
        struct = parser.get_structure(model_path.name, fh)

    residues = Bio.PDB.Selection.unfold_entities(entity_list=struct[0], target_level='R')
    for resid in residues:
        chain, chain_id = resid.get_parent(), resid.get_parent().get_id()
        hetflag, resseq, icode = resid.get_id()

        corrected_id = mapping.loc[(chain_id, resseq), 'id']
        corrected_pos = mapping.loc[(chain_id, resseq), 'pos']

        #print(resid, chain, chain_id, '!', hetflag, '!', resseq, icode, corrected_id, corrected_pos)

        # Detach residue from modified chain
        chain.detach_child(resid.get_id())

        # Seems that can change resseq by re-writing id tuple as a whole..
        # Set hetflag to a single space for an ATOM record
        resid.id = (' ', int(corrected_pos), icode)

        # Add residue to original chain
        struct[0][corrected_id].add(resid)

    # Generate list of emtpy chains in struct
    empty_chain_id = []
    for chain in Bio.PDB.Selection.unfold_entities(entity_list=struct[0], target_level='C'):
        if len(list(chain.get_residues())) == 0:
            empty_chain_id.append(chain.id)

    # Remove empty chains from struct
    for chain_id in empty_chain_id:
        struct[0].detach_child(chain_id)

    io = Bio.PDB.PDBIO()
    #io = Bio.PDB.MMCIFIO()
    io.set_structure(struct)
    io.save(str(corrected_model_path))

def process_json_files(source_path: Path, output_path: Path, mapping_path: Path = None, predict_path: Path = None) -> None:
    """
    Process all JSON files in the source directory and create modified versions.
    Optionally saves the final residue mapping for each file if residue_mapping_dir is specified.
    
    Args:
        source_path: Directory containing original JSON files
        output_path: Directory to save modified JSON files
        mapping_path: Directory to save residue mapping JSON files (optional)
    """
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    #if mapping_path:
    #    mapping_path.mkdir(parents=True, exist_ok=True)

    # Process files
    for json_path in source_path.glob('*.json'):
        #if not(json_path.stem in {'5EDV_polybonds', '5EDV_seqonly', '6xbe_polybonds', '6xbe_seqonly',}):
        #    print(json_path.stem, 'skipping')
        #    continue

        modified_json_path = output_path / json_path.name
        tsv_mapping_path = mapping_path / json_path.with_suffix('.tsv').name
        cif_path = predict_path / json_path.stem / f'{json_path.stem}_model.cif.gz'
        mod_path = predict_path / json_path.stem / f'{json_path.stem}_model_corrected.pdb'

        if not modified_json_path.is_file():
            try:
                with open(json_path, 'r') as fh:
                    json_data = json.load(fh)
                print(f"Loaded: {json_path.name}")
            except Exception as e:
                print(f"Error loading {json_path.name}: {e}")

            # Generate mapping
            print(f"Processing {json_path.name}...")
            residue_mapping = generate_residue_mapping(json_data)

            # Use mapping to generate modified json and write to file
            modified_json = generate_modified_json(json_data, residue_mapping)
            with open(modified_json_path, 'w') as f:
                json.dump(modified_json, f, indent=2)
            print(f"Saved modified file: {modified_json_path}")

            # Write mapping
            #residue_mapping.to_csv(tsv_mapping_path, sep='\t')
            #print(f"Saved residue mapping: {tsv_mapping_path}")

        elif cif_path.is_file() and not mod_path.is_file():
            print(f"Post-processing structure:", cif_path)
            residue_mapping = pd.read_csv(tsv_mapping_path, sep='\t').set_index(['modified_id', 'modified_pos'])
            with open(modified_json_path, 'r') as fh:
                modified_json = json.load(fh)
            post_process_structure(cif_path, mod_path, residue_mapping)
            print(f"Wrote output to:", mod_path)

def main():
    """
    Main function to execute the protein bond modeling script.
    """
    parser = argparse.ArgumentParser(
        description="Model protein-protein bonds using ligand bridges in AlphaFold3 JSON files"
    )
    parser.add_argument(
        "--source_path", 
        "-s", 
        default="input/",
        help="Directory containing input JSON files (default: input/)"
    )
    parser.add_argument(
        "--output_path", 
        "-o", 
        default="output/",
        help="Directory to save modified JSON files (default: output/)"
    )
    #parser.add_argument(
    #    "--mapping_dir",
    #    default=None,
    #    help="Directory to save residue mapping JSON files (optional)"
    #)
    #parser.add_argument(
    #    "--predict_dir",
    #    default=None,
    #    help="Directory of AlphaFold3 predictions (optional)"
    #)
    
    args = parser.parse_args()
    print(f"alphafold3-polymer-bonds v{importlib.metadata.version('alphafold3-polymer-bonds')}")
    print(f"Source file: {args.source_path}")
    print(f"Output file: {args.output_path}")

    with open(args.source_path, 'r') as fh:
        json_data = json.load(fh)
        print(f"Loaded: {args.source_path}")

    # Generate mapping
    #print(f"Processing {json_path.name}...")
    residue_mapping = generate_residue_mapping(json_data)

    # Use mapping to generate modified json and write to file
    modified_json = generate_modified_json(json_data, residue_mapping)
    with open(args.output_path, 'w') as f:
        json.dump(modified_json, f, indent=2)
    print(f"Saved modified file: {args.output_path}")

    #if args.mapping_dir:
    #    print(f"Residue mapping directory: {args.mapping_dir}")
    #if args.predict_dir:
    #    print(f"AlphaFold3 predictions directory: {args.predict_dir}")
    
    # Check if source directory exists
    #if not Path(args.source_dir).exists():
    #    print(f"Error: Source directory '{args.source_dir}' does not exist!")
    #    return 1
    
    # Process all JSON files
    #process_json_files(Path(args.source_dir), Path(args.output_dir), Path(args.mapping_dir), Path(args.predict_dir))
    #print("Process completed successfully!")
