VIRULENCE_DB = {
    "Shiga Toxin (stx1)": "GAATAAATTTTTGTC",
    "Hemolysin (hlyA)": "TGCAGGCTGGAGCT",
    "Intimin (eae)": "ATTGATAGGAACTTA"
}

def predict_virulence(sequence: str):
    factors = []
    score = 0

    for factor, motif in VIRULENCE_DB.items():
        if motif in sequence:
            factors.append(factor)
            score += 25  # Arbitrary severity score
    
    # Normalize score
    final_score = min(score, 100)
    
    return {
        "virulenceScore": final_score,
        "factors": factors
    }