### ProteoKit

ProteoKit is a Python package for fetching and searching protein sequences from UniProt.

#### Installation

```bash
pip install proteokit
```
#### Usage
```bash
from proteokit import protein_read, protein_print, protein_search, print_search_results

header, seq, length = protein_read("P69905")
protein_print("P69905")

results = protein_search("hemoglobin")
print_search_results(results)
```
