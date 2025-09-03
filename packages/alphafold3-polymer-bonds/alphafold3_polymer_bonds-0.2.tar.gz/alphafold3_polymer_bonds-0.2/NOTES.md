# NOTES
- Coordinates in AlphaFold3 input are 1-based (e.g. `ptmType`, `bondedAtomPairs`)
- To introduce an atom-level representation of a residue for covalent bond definition, use `ptmType`/`userCcd` to define a ligand that's identical to the standard amino acid
[alphafold3#159](https://github.com/google-deepmind/alphafold3/issues/159#issuecomment-2525070335)
- Leaving atoms for polymer-ligand covalent bonds were kept when training AlphaFold3 
[alphafold3#159](https://github.com/google-deepmind/alphafold3/issues/159#issuecomment-2523711478)
- Cif is heterogenous format, mandatory fields for AlphaFold3 ligands are documented in
[alphafold3#178](https://github.com/google-deepmind/alphafold3/issues/178#issuecomment-2521175288)
- Modified residues need to have the following atoms: `N`, `CA`, `C`, `O`, `OXT`
[alphafold3#159](https://github.com/google-deepmind/alphafold3/issues/159#issuecomment-2561311898)
- Cif files can include information on leaving atoms but AlphaFold3 ignores this
[alphafold3#250](https://github.com/google-deepmind/alphafold3/issues/159#issue-2712293489)
- Leaving atoms are harmless as the model does not seem to use them
[alphafold3#250](https://github.com/google-deepmind/alphafold3/issues/250#issuecomment-2580322870)
- Warnings about `does not contain a pseudo-beta atom` described as safe to ignore
[alphafold3#438](https://github.com/google-deepmind/alphafold3/issues/438#issuecomment-2955474005)
- AlphaFold server allows for modifications for
[residues](https://github.com/google-deepmind/alphafold/tree/main/server#protein-chains),
[DNA](https://github.com/google-deepmind/alphafold/tree/main/server#dna-chains),
[RNA](https://github.com/google-deepmind/alphafold/tree/main/server#rna-chains)
- Install development version:
    ```
    git clone git@github.com:jurgjn/alphafold3-polymer-bonds.git
    cd alphafold3-polymer-bonds
    pip install -e .
    ```
- Uninstall development version:
    ```
    pip uninstall alphafold3-polymer-bonds
    ```

## Residue/nucleotide atom names
All residues and nucleotides are in the CCD, tables below give links to residues/nucleotides in [PDBeChem](https://www.ebi.ac.uk/msd-srv/msdchem/cgi-bin/cgi.pl). This is useful to look up atom names that can then be used to specify covalent bonds in `BondedAtomPairs`.

| Residue       | Character | Ligand |
| ------------- | --------- | ------ |
| alanine       | A         | [ALA](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/ALA) |
| arginine      | R         | [ARG](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/ARG) |
| asparagine    | N         | [ASN](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/ASN) |
| aspartic acid | D         | [ASP](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/ASP) |
| cysteine      | C         | [CYS](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/CYS) |
| glutamine     | Q         | [GLN](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/GLN) |
| glutamic acid | E         | [GLU](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/GLU) |
| glycine       | G         | [GLY](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/GLY) |
| histidine     | H         | [HIS](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/HIS) |
| isoleucine    | I         | [ILE](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/ILE) |
| leucine       | L         | [LEU](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/LEU) |
| lysine        | K         | [LYS](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/LYS) |
| methionine    | M         | [MET](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/MET) |
| phenylalanine | F         | [PHE](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/PHE) |
| proline       | P         | [PRO](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/PRO) |
| serine        | S         | [SER](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/SER) |
| threonine     | T         | [THR](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/THR) |
| tryptophan    | W         | [TRP](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/TRP) |
| tyrosine      | Y         | [TYR](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/TYR) |
| valine        | V         | [VAL](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/VAL) |

| Nucleotide      | Character | DNA ligand | RNA ligand |
| --------------- | --------- | ---------- | ---------- |
| adenine         | A         | [DA](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/DA) | [A](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/A) |
| guanine         | G         | [DG](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/DG) | [C](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/C) |
| cytosine        | C         | [DC](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/DC) | [G](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/G) |
| thymine/uracil  | T/U       | [DT](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/DT) | [U](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/U) |
