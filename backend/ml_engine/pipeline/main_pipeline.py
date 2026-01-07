import random
from ml_engine.feature_extraction import sequence_stats, orf_finder, motif_scanner
from ml_engine.models import risk_model, resistance_model, virulence_model

def parse_fasta_if_needed(content: str) -> str:
    """Helper to clean FASTA headers if present"""
    lines = content.strip().split('\n')
    sequence = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith(">"):
            continue
        sequence.append(line)
    return "".join(sequence).upper()

def run_analysis_pipeline(sequence: str):
    # 1. Clean Sequence
    clean_seq = parse_fasta_if_needed(sequence)
    
    # 2. Feature Extraction
    seq_stats = sequence_stats.get_basic_stats(clean_seq)
    orf_data = orf_finder.find_orfs(clean_seq)
    crispr_data = motif_scanner.scan_crispr(clean_seq)
    
    # 3. Model Inference
    # A. Resistance
    res_results = resistance_model.predict_resistance(clean_seq, orf_data["orfs"])
    
    # B. Virulence
    vir_results = virulence_model.predict_virulence(clean_seq)
    
    # C. Risk Models (Pathogenicity & HGT)
    pathogen_risk = risk_model.calculate_pathogenic_risk(
        genome_len=seq_stats["length"],
        gc=seq_stats["gc_content"],
        orf_count=orf_data["orf_count"],
        res_count=res_results["totalResistanceGenes"],
        vir_score=vir_results["virulenceScore"],
        crispr_present=crispr_data["present"]
    )
    
    hgt_results = risk_model.calculate_hgt_risk(
        gc_content=seq_stats["gc_content"],
        orf_count=orf_data["orf_count"],
        res_count=res_results["totalResistanceGenes"]
    )

    # 4. Protein Structure Mock (Preserving your optional feature)
    # Simulating a protein structure for the longest ORF if it exists
    protein_structure = None
    if orf_data["orfs"]:
        protein_structure = {
            "structure_id": f"PZ-{random.randint(1000, 9999)}",
            "confidence_score": round(random.uniform(75.0, 98.5), 2),
            "molecular_weight": f"{round(len(orf_data['orfs'][0]) * 0.11, 2)} kDa",
            "folding_type": "Alpha-Helix Dominant",
            "description": "Predicted transmembrane domain with high stability."
        }
    
    # 5. Construct Final JSON (Matched to Frontend expectation)
    # Note: We map the new rigorous ML outputs to the simplified frontend format
    explanation = (
        f"The genome has a GC content of {seq_stats['gc_content']}%. "
        f"Analysis identified {res_results['totalResistanceGenes']} potential resistance markers. "
        f"Pathogenic risk is calculated as {pathogen_risk['pathogenicRisk']} ({pathogen_risk['riskScore']}/100)."
    )

    output_payload = {
        "metadata": {
            "length": seq_stats["length"],
            "gc_content": seq_stats["gc_content"],
            "orf_count": orf_data["orf_count"]
        },
        "resistance_genes": res_results["genes"],
        "crispr_status": "Present" if crispr_data["present"] else "Absent",
        "risk_score": pathogen_risk["riskScore"] / 100.0, # Frontend expects 0.0-1.0
        "risk_level": pathogen_risk["pathogenicRisk"],
        "explanation": explanation,
        "protein_structure": protein_structure,
        
        # Extra ML details (can be used later)
        "advanced_ml": {
            "virulence": vir_results,
            "hgt_risk": hgt_results
        }
    }
    
    return output_payload