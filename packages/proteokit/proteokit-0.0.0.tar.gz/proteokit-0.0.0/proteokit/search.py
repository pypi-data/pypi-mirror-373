import requests

def protein_search(keyword):
    """Search UniProt by keyword."""
    url = f"https://rest.uniprot.org/uniprotkb/search?query={keyword}&format=json&size=5"
    
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Search failed: {r.status_code}")
    
    results = r.json().get("results", [])
    hits = []
    for entry in results:
        hits.append({
            "id": entry.get("primaryAccession", "N/A"),
            "gene": entry.get("genes", [{}])[0].get("geneName", {}).get("value", "N/A"),
            "organism": entry.get("organism", {}).get("scientificName", "Unknown")
        })
    return hits

def print_search_results(results):
    """Print formatted search results from protein_search()."""
    if not results:
        print("No results found.")
        return

    print(f"\nFound {len(results)} result(s):\n")
    for i, r in enumerate(results, 1):
        print(f"[{i}] UniProt ID : {r['id']}")
        print(f"    Gene       : {r['gene']}")
        print(f"    Organism   : {r['organism']}\n")
