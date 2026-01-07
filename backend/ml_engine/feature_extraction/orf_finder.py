def find_orfs(sequence: str, min_len=100):
    """
    Finds ORFs (Start ATG -> Stop TAA/TAG/TGA).
    """
    start_codon = "ATG"
    stop_codons = {"TAA", "TAG", "TGA"}
    orfs = []
    seq_len = len(sequence)
    
    i = 0
    while i < seq_len - 2:
        if sequence[i:i+3] == start_codon:
            for j in range(i + 3, seq_len - 2, 3):
                codon = sequence[j:j+3]
                if codon in stop_codons:
                    orf_seq = sequence[i:j+3]
                    if len(orf_seq) >= min_len:
                        orfs.append(orf_seq)
                    i = j # Move pointer
                    break
        i += 1

    count = len(orfs)
    avg_len = sum(len(o) for o in orfs) / count if count > 0 else 0

    return {
        "orf_count": count,
        "average_orf_length": round(avg_len, 1),
        "orfs": orfs # Only used internally
    }