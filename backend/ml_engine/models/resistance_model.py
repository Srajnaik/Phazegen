# Mock database of resistance motifs
RESISTANCE_DB = {
    "mecA (Methicillin)": "TCCAGATTACAACTTCACCAGGTTCACT",
    "blaKPC (Carbapenem)": "ATGTCACTGTATCGCCGTCTAGTTCT",
    "vanA (Vancomycin)": "AATAGTTGTTGCCTTGCCGGAGAT",
    "tetM (Tetracycline)": "GGCACAGATGGTAGCAGAGATAA"
}

def predict_resistance(sequence: str, orf_data: list):
    found_genes = []
    
    # 1. Direct Motif Search (High Confidence)
    for gene, motif in RESISTANCE_DB.items():
        if motif in sequence:
            found_genes.append({"gene": gene, "class": "Antibiotic Resistance", "confidence": 0.95})

    # 2. GC-Skew based Anomaly Detection (Low Confidence)
    # If a specific short marker "GATACA" is found (demo trigger)
    if "GATACA" in sequence: 
         found_genes.append({"gene": "Unknown Beta-Lactamase", "class": "Beta-Lactam", "confidence": 0.65})

    return {
        "totalResistanceGenes": len(found_genes),
        "genes": found_genes
    }