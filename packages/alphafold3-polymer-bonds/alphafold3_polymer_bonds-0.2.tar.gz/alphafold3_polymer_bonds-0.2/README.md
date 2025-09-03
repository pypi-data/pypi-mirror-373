[![PyPI - Version](https://img.shields.io/pypi/v/alphafold3-polymer-bonds)](https://pypi.org/project/alphafold3-polymer-bonds/)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/alphafold3-polymer-bonds?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/alphafold3-polymer-bonds)
![GitHub License](https://img.shields.io/github/license/jurgjn/alphafold3-polymer-bonds)

# Polymer bonds in AlphaFold3
AlphaFold3
[does not allow](https://github.com/google-deepmind/alphafold3/blob/main/docs/input.md#bonds)
covalent bonds between/within polymer chains (protein, DNA, RNA).
We work around this limitation by treating one of the corresponding residue or nucleic acid as a modified residue/amino-acid.
AlphaFold3 can, in many cases, infer the bonds from context. See below for cases where this matters. 
In principle, this may enable AlphaFold3 to explicitly model e.g. disulfide bonds, cyclic peptides, zero-length crosslinkers, protein-DNA bonds..

*This is currently exploratory, see below for specifc examples. Also take a look at complementary work:
[KosinskiLab/af3x](https://github.com/KosinskiLab/af3x)
and
[bio-phys/polyUb-AF](https://github.com/bio-phys/polyUb-AF).*

![1AAR](examples/visualise/1AAR.png)
1AAR with (left, RMSD<1) vs without (right, RMSD>10) covalent bond between Lys48 and Gly76, AlphaFold3 run without templates

## Quick start
```bash
pip install alphafold3-polymer-bonds
alphafold3_polymer_bonds --help
```

