import requests

def protein_read(uniprot_id):
    """Fetch protein FASTA by UniProt ID and return header, sequence, and length."""
    url = f"https://rest.uniprot.org/uniprotkb/{uniprot_id}.fasta"
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Could not fetch UniProt ID: {uniprot_id}")
    lines = r.text.strip().split('\n')
    header = lines[0][1:]
    seq = ''.join(lines[1:])
    return header, seq, len(seq)

def protein_write(uniprot_id, file_path):
    """Fetch and write protein FASTA to a file."""
    header, seq, _ = protein_read(uniprot_id)
    with open(file_path, 'w') as f:
        f.write(f">{header}\n")
        for i in range(0, len(seq), 60):
            f.write(seq[i:i+60] + '\n')

def protein_print(uniprot_id):
    """Print protein header and sequence to console."""
    header, seq, length = protein_read(uniprot_id)
    print(f">{header}\n{seq}\nLength: {length}")
