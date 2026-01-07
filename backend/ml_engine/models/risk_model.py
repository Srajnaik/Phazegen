import joblib
import numpy as np
import os

# Load the trained model GLOBALLY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "pathogen_risk_rf.pkl")

try:
    REAL_MODEL = joblib.load(MODEL_PATH)
    print("✅ Loaded REAL Random Forest Model")
except:
    print("⚠️ Model file not found. Using fallback logic.")
    REAL_MODEL = None

def calculate_pathogenic_risk(genome_len, gc, orf_count, res_count, vir_score, crispr_present):
    """
    Uses TRAINED Random Forest Model if available.
    """
    if REAL_MODEL:
        # 1. PREPARE FEATURES
        # The model expects exactly 6 columns in this order:
        # [genome_length, gc_content, orf_count, resistance_gene_count, virulence_factor_count, crispr_present]
        
        # approximate factor count from score (since score = count * 25 in virulence_model.py)
        vir_count = int(vir_score / 25) 
        
        # Convert boolean to integer (True -> 1, False -> 0)
        is_crispr = 1 if crispr_present else 0
        
        input_features = np.array([[
            genome_len, 
            gc, 
            orf_count, 
            res_count, 
            vir_count, 
            is_crispr
        ]])
        
        # 2. PREDICT
        # Predict Class (Low/High)
        prediction = REAL_MODEL.predict(input_features)[0]
        
        # Predict Probability (Risk Score 0-100)
        probs = REAL_MODEL.predict_proba(input_features)
        
        # Get probability of the "High" class (usually index 1)
        # We perform a safe check to see which index corresponds to "High"
        class_labels = list(REAL_MODEL.classes_)
        high_index = class_labels.index("High") if "High" in class_labels else 1
        
        risk_score = int(probs[0][high_index] * 100)
        
        return {
            "pathogenicRisk": prediction,
            "riskScore": risk_score,
            "confidence": "High (RF Model)"
        }
        
    else:
        # --- FALLBACK LOGIC (For when model is missing) ---
        score = 10 + (res_count * 20) + (vir_score * 0.5)
        if 40 <= gc <= 60: score += 5
        final_score = min(round(score), 100)
        label = "Low"
        if final_score > 40: label = "Medium"
        if final_score > 75: label = "High"
        
        return {
            "pathogenicRisk": label,
            "riskScore": final_score,
            "confidence": "Low (Heuristic)"
        }

def calculate_hgt_risk(gc_content, orf_count, res_count):
    # Heuristic logic for HGT
    hgt_score = (res_count * 15) + (abs(gc_content - 50.0) * 2)
    hgt_score = min(round(hgt_score), 100)
    
    risk_label = "Low"
    if hgt_score > 30: risk_label = "Medium"
    if hgt_score > 60: risk_label = "High"
    
    return {
        "risk": risk_label,
        "score": hgt_score
    }