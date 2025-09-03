# ProteinPy

A Python toolkit for fetching and analyzing protein sequences.

## Features

- **Sequence Retrieval**  
  Retrieve protein sequences directly from the UniProt Knowledgebase via accession IDs.

- **Biochemical Property Analysis**  
  Calculate key biochemical properties such as:  
  - Molecular weight  
  - Isoelectric point (pI)  
  - GRAVY (Grand Average of Hydropathicity)  
  - Aromaticity  
  - Aliphatic index  

- **Sequence Manipulation**  
  - Extract sub-sequences and generate sliding k-mers  
  - Perform amino acid mutations (single or batch)  
  - Identify sequence motifs using custom regular expressions  

- **Data Export**  
  Export sequences in FASTA format and analytical results in JSON or CSV.

- **Visualization**  
  Create amino acid composition and distribution plots using Matplotlib.

- **Reporting**  
  Generate clear, user-friendly summary reports for quick interpretation.

---




## Installation

```bash
pip install proteinpy

```


## Example Usage

```bash
from proteinpy import Protein

# Initialize a protein object with a UniProt accession
p = Protein("P69905")  # Hemoglobin alpha subunit

# Fetch and print summary statistics
p.summary()

# Get amino acid counts and visualize them
p.aa_counts()
p.aa_distribution()

# Simulate a mutation at position 42
mutated_seq = p.mutate(42, "K")

# Find a motif using regex
positions = p.find_motif("N[^P][ST][^P]")

# Export as JSON or CSV
p.to_json()
p.to_csv("P69905.csv")


```
