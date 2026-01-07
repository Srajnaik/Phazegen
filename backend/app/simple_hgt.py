import re
import json
import tempfile
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import uvicorn
from datetime import datetime

app = FastAPI(title="PhazeGEN HGT API - Simplified")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    sequence: str
    filename: str = "unknown"

class SimplifiedHGTAnalyzer:
    def __init__(self):
        # Pre-defined patterns for demonstration
        self.patterns = {
            'plasmids': {
                'IncF': r'ATG[ACGT]{15,}AAA[ACGT]{10,}TAA',
                'IncI': r'ATG[ACGT]{12,}GGT[ACGT]{8,}TGA',
                'repA': r'ATG[ACGT]{18,}CAG[ACGT]{9,}TAA',
                'parA': r'ATG[ACGT]{10,}TTC[ACGT]{7,}TAG',
            },
            'transposons': {
                'tnpA': r'ATG[ACGT]{20,}CAT[ACGT]{10,}TAA',
                'IS3': r'CAGGTA|GTCCAT',
                'IS5': r'GGTTAC|CCAATG',
                'tnpR': r'ATG[ACGT]{15,}GGA[ACGT]{8,}TGA',
            },
            'resistance': {
                'blaTEM': r'ATG[ACGT]{30,}S[ACGT]{10,}ESBL',
                'tetA': r'ATG[ACGT]{25,}MFS[ACGT]{15,}TAA',
                'aac': r'ATG[ACGT]{20,}AAC[ACGT]{10,}TGA',
                'mcr': r'ATG[ACGT]{18,}MCR[ACGT]{12,}TAA',
            }
        }
    
    def analyze(self, sequence: str) -> Dict:
        sequence = sequence.upper()
        detections = []
        
        for category, patterns in self.patterns.items():
            for name, pattern in patterns.items():
                matches = list(re.finditer(pattern, sequence, re.IGNORECASE))
                if matches:
                    for match in matches:
                        detections.append({
                            'type': category[:-1] if category.endswith('s') else category,
                            'name': name,
                            'position': f"{match.start()}-{match.end()}",
                            'confidence': min(0.7 + (len(match.group()) / 100), 0.95),
                            'sequence': match.group()[:50] + '...' if len(match.group()) > 50 else match.group()
                        })
        
        # Calculate risk score
        risk_score = self.calculate_risk(detections)
        
        return {
            'status': 'success',
            'detections': detections,
            'detected_elements': {
                'plasmids': [d for d in detections if d['type'] == 'plasmid'],
                'transposons': [d for d in detections if d['type'] == 'transposon'],
                'resistance_genes': [d for d in detections if d['type'] == 'resistance']
            },
            'risk_score': risk_score,
            'risk_level': self.get_risk_level(risk_score),
            'sequence_length': len(sequence),
            'sample_id': f"HGT-{int(datetime.now().timestamp())}",
            'recommendations': self.get_recommendations(detections, risk_score)
        }
    
    def calculate_risk(self, detections: List[Dict]) -> int:
        score = 0
        for d in detections:
            if d['type'] == 'plasmid':
                score += 15
                if d['name'] in ['IncF', 'IncI']:
                    score += 10
            elif d['type'] == 'transposon':
                score += 10
                if d['name'] in ['tnpA', 'tnpR']:
                    score += 5
            elif d['type'] == 'resistance':
                score += 20
                if d['name'] in ['blaTEM', 'mcr']:
                    score += 15
            
            score += int(d['confidence'] * 10)
        
        return min(score, 100)
    
    def get_risk_level(self, score: int) -> str:
        if score >= 70: return 'Critical'
        elif score >= 50: return 'High'
        elif score >= 30: return 'Medium'
        elif score >= 10: return 'Low'
        else: return 'Minimal'
    
    def get_recommendations(self, detections: List[Dict], score: int) -> List[str]:
        recs = []
        
        if score >= 50:
            recs.append("🚨 High spread risk detected - implement containment measures")
        
        if any(d['type'] == 'plasmid' for d in detections):
            recs.append("⚠️ Mobile genetic elements (plasmids) detected")
        
        if any(d['type'] == 'resistance' for d in detections):
            recs.append("💊 Antibiotic resistance genes present")
            
        if any(d['name'] == 'mcr' for d in detections):
            recs.append("🦠 Colistin resistance (mcr) detected - high clinical concern")
        
        if not recs:
            recs.append("✅ No significant HGT risk elements detected")
        
        recs.append("🔬 Consider experimental validation for confirmation")
        return recs

analyzer = SimplifiedHGTAnalyzer()

@app.get("/")
def root():
    return {"message": "PhazeGEN HGT Risk Detection API", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/api/analyze")
async def analyze_sequence(request: AnalysisRequest):
    try:
        if len(request.sequence) < 20:
            raise HTTPException(400, "Sequence too short")
        
        result = analyzer.analyze(request.sequence)
        result['filename'] = request.filename
        
        return result
    except Exception as e:
        raise HTTPException(500, f"Analysis failed: {str(e)}")

@app.post("/api/analyze/file")
async def analyze_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        sequence = content.decode('utf-8')
        
        if not sequence:
            raise HTTPException(400, "Empty file")
        
        result = analyzer.analyze(sequence)
        result['filename'] = file.filename
        
        return result
    except Exception as e:
        raise HTTPException(500, f"File analysis failed: {str(e)}")

@app.get("/api/test")
def test_endpoint():
    """Test with sample sequence"""
    sample = (
        "ATGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC"
        "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC"
        "CAGGTAATCGATCGATCGATCGATCGATCGATCGATCGATCGA"
        "TGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
        "ATGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC"
    )
    
    return analyzer.analyze(sample)

if __name__ == "__main__":
    print("Starting simplified HGT analyzer...")
    print("API: http://localhost:8000")
    print("Test: http://localhost:8000/api/test")
    print("Health: http://localhost:8000/health")
    uvicorn.run(app, host="0.0.0.0", port=8000)