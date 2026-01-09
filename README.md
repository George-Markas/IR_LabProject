# IR LabProject 2025-2026
This is a toy search engine using the Reuters-21578 Corpus dataset,
for the "Information Retrieval" course assignment.

## Set up and run
The following dependencies are needed:
- python 3.10+
- venv
- make (optional, recommended for easy setup)

With make:
```sh
git clone https://github.com/George-Markas/IR_LabProject.git
cd IR_LabProject

# This will set up the virtual environment and run the search engine
make

# Remove artifacts when done
make clean
```
Manually:
```sh
git clone https://github.com/George-Markas/IR_LabProject.git
cd IR_LabProject

# Set up the virtual environment
python3 -m venv venv
./venv/bin/pip install -e .

# Run the search engine
./venv/bin/search-engine-cli
```