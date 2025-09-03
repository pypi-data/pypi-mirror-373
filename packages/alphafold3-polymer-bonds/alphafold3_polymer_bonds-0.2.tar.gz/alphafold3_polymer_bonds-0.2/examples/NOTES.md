## Run AlphaFold3 on Google Colab (Pro)
- Does everything that the web server can't, e.g. can input any ligand
- Installs on the Colab runtime by reproducing steps from the official [Dockerfile](https://github.com/google-deepmind/alphafold3/tree/main)
- Passes built-in unit tests (run_alphafold_test.py and run_alphafold_data_test.py)

**Limitations:**
- Not enough disk space for the sequence databases, need to use MSAs obtained elsewhere
- GPU RAM restricts input size