import pandas as pd
import numpy as np

def generate_synthetic_data(num_samples=10000):
    print(f"Generating {num_samples} synthetic bacterial genomes...")
    np.random.seed(42)  # For reproducible results

    # 1. Initialize empty DataFrame
    data = {
        'genome_length': [],
        'gc_content': [],
        'orf_count': [],
        'resistance_gene_count': [],
        'virulence_factor_count': [],
        'crispr_present': [],
        'label': []  # 0 = Low Risk, 1 = High Risk (Pathogenic)
    }

    for _ in range(num_samples):
        # Decide if this sample is Pathogenic (30% chance) or Non-Pathogenic (70%)
        is_pathogen = np.random.choice([0, 1], p=[0.7, 0.3])

        if is_pathogen:
            # --- PATHOGENIC PROFILE ---
            # Pathogens often have pathogenicity islands, leading to slightly larger genomes sometimes
            length = int(np.random.normal(loc=4.8e6, scale=0.5e6)) 
            
            # GC Content: Some pathogens (like Pseudomonas) have high GC, others low. 
            # We'll randomize it but keep it slightly distinct for the ML to learn.
            gc = np.random.normal(loc=52, scale=4)
            
            # Resistance Genes: Pathogens are much more likely to have resistance
            res_count = np.random.poisson(lam=3.5) # Average 3.5 genes
            
            # Virulence Factors: The defining feature of pathogens
            vir_count = np.random.poisson(lam=4.0)
            
            # CRISPR: Sometimes inversely correlated with AMR acquisition (controversial, but useful for ML pattern)
            crispr = np.random.choice([0, 1], p=[0.6, 0.4]) 
            
            label = "High"
        
        else:
            # --- NON-PATHOGENIC (COMMENSAL) PROFILE ---
            length = int(np.random.normal(loc=3.5e6, scale=0.5e6))
            gc = np.random.normal(loc=48, scale=6)
            
            # Commensals usually have few/no resistance genes
            res_count = np.random.poisson(lam=0.5) 
            
            # Very few virulence factors
            vir_count = np.random.poisson(lam=0.2)
            
            # CRISPR often present to defend against phages
            crispr = np.random.choice([0, 1], p=[0.3, 0.7])
            
            label = "Low"

        # ORF Count is strictly correlated to genome length (approx 1 gene per 1000bp)
        orf_count = int(length / 950) + np.random.randint(-50, 50)

        # Append to data
        data['genome_length'].append(abs(length))
        data['gc_content'].append(abs(gc))
        data['orf_count'].append(abs(orf_count))
        data['resistance_gene_count'].append(abs(res_count))
        data['virulence_factor_count'].append(abs(vir_count))
        data['crispr_present'].append(crispr)
        data['label'].append(label)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv("bacteria_train_data.csv", index=False)
    print("✅ Success! 'bacteria_train_data.csv' created with 10,000 rows.")
    return df

if __name__ == "__main__":
    generate_synthetic_data()