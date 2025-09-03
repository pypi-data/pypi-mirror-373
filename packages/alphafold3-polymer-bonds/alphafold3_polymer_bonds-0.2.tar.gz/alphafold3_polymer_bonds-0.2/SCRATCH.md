## [Unreleased]

### Added
- Examples, all running on Google Colab (Pro)
- Only include custom ligands that are actually used in `userCCD`
- Publish package on conda-forge
---

- Fix `does not contain a pseudo-beta atom.Using first valid atom (CD) instead`
- Note that atom_name is empty..
      dtype=object))), does not contain a pseudo-beta atom.Using first valid atom (CD) instead.
W0829 16:12:34.273248 22653824512768 features.py:1410] 1AAR_polybonds, random_seed=1 token 127 (AtomLayout(atom_name=array([['CE', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '',
        '', '', '', '', '', '', '', '']], dtype=object), res_id=array([[48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48,
        48, 48, 48, 48, 48, 48, 48, 48]]), chain_id=array([['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B',
        'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']],

### Added
- Examples: diubiquitin (1AAR), cyclic peptide (8J3S), cyclic RNA (8S6W)