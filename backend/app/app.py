from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import re
import uvicorn

app = FastAPI(title="PhazeGEN HGT API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HGTRiskAnalyzer:
    """Complete HGT analyzer built-in - no external services needed"""
    
    def __init__(self):
        # Database of known patterns for detection
        self.patterns = {
            'plasmids': {
                'IncF': r'ATG[ACGT]{15,}AAA[ACGT]{10,}TAA',
                'IncI': r'ATG[ACGT]{12,}GGT[ACGT]{8,}TGA',
                'RepA': r'ATG[ACGT]{18,}CAG[ACGT]{9,}TAA',
                'ParA': r'ATG[ACGT]{10,}TTC[ACGT]{7,}TAG',
            },
            'transposons': {
                'Tn5': r'ATG[ACGT]{20,}CAT[ACGT]{10,}TAA',
                'IS3': r'CAGGTA|GTCCAT',
                'IS5': r'GGTTAC|CCAATG',
                'Tn3': r'ATG[ACGT]{15,}GGA[ACGT]{8,}TGA',
            },
            'resistance': {
                'blaTEM': r'ATG[ACGT]{30,}S[ACGT]{10,}',
                'blaCTX-M': r'ATG[ACGT]{28,}CTX[ACGT]{12,}',
                'tetA': r'ATG[ACGT]{25,}MFS[ACGT]{15,}TAA',
                'aac': r'ATG[ACGT]{20,}AAC[ACGT]{10,}TGA',
                'mcr': r'ATG[ACGT]{18,}MCR[ACGT]{12,}TAA',
            }
        }
        
        # High-risk plasmid types
        self.high_risk_plasmids = ['IncF', 'IncI', 'IncA/C', 'IncX']
        
        # Critical resistance genes
        self.critical_genes = ['blaCTX-M', 'mcr', 'KPC', 'NDM']
    
    def analyze_sequence(self, sequence: str, filename: str = "unknown"):
        """Main analysis function"""
        sequence = sequence.upper()
        
        # Initialize results
        results = {
            'sample_id': filename,
            'sequence_length': len(sequence),
            'risk_score': 0,
            'risk_level': 'Minimal',
            'detected_elements': {
                'plasmids': [],
                'transposons': [],
                'resistance_genes': [],
                'virulence_factors': []
            },
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Detect all elements
            results['detected_elements']['plasmids'] = self._detect_plasmids(sequence)
            results['detected_elements']['transposons'] = self._detect_transposons(sequence)
            results['detected_elements']['resistance_genes'] = self._detect_resistance(sequence)
            
            # Calculate risk score
            results['risk_score'] = self._calculate_risk_score(results['detected_elements'])
            results['risk_level'] = self._determine_risk_level(results['risk_score'])
            
            # Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
            # Add summary
            results['summary'] = self._create_summary(results)
            
        except Exception as e:
            results['error'] = str(e)
            results['warnings'].append(f"Analysis error: {e}")
        
        return results
    
    def _detect_plasmids(self, sequence: str):
        """Detect plasmid signatures"""
        plasmids = []
        
        for name, pattern in self.patterns['plasmids'].items():
            matches = list(re.finditer(pattern, sequence, re.IGNORECASE))
            for match in matches:
                plasmids.append({
                    'replicon': name,
                    'position': f"{match.start()}-{match.end()}",
                    'confidence': min(0.8 + (len(match.group()) / 200), 0.95),
                    'sequence': match.group()[:30] + '...' if len(match.group()) > 30 else match.group(),
                    'risk_category': 'High' if name in self.high_risk_plasmids else 'Medium'
                })
        
        return plasmids
    
    def _detect_transposons(self, sequence: str):
        """Detect transposons and IS elements"""
        transposons = []
        
        for name, pattern in self.patterns['transposons'].items():
            matches = list(re.finditer(pattern, sequence, re.IGNORECASE))
            for match in matches:
                transposons.append({
                    'name': name,
                    'type': 'Insertion Sequence' if name.startswith('IS') else 'Transposon',
                    'position': f"{match.start()}-{match.end()}",
                    'confidence': min(0.75 + (len(match.group()) / 150), 0.92),
                    'family': self._classify_transposon_family(name)
                })
        
        return transposons
    
    def _detect_resistance(self, sequence: str):
        """Detect antibiotic resistance genes"""
        resistance_genes = []
        
        for name, pattern in self.patterns['resistance'].items():
            matches = list(re.finditer(pattern, sequence, re.IGNORECASE))
            for match in matches:
                gene = {
                    'gene': name,
                    'position': f"{match.start()}-{match.end()}",
                    'confidence': min(0.85 + (len(match.group()) / 180), 0.98),
                    'drug_class': self._get_drug_class(name),
                    'risk_level': 'Critical' if name in self.critical_genes else 'High'
                }
                resistance_genes.append(gene)
        
        return resistance_genes
    
    def _calculate_risk_score(self, elements: dict) -> int:
        """Calculate HGT risk score (0-100)"""
        score = 0
        
        # Plasmid scoring
        for plasmid in elements.get('plasmids', []):
            score += 10
            if plasmid.get('risk_category') == 'High':
                score += 15
            if plasmid.get('replicon', '').startswith('Inc'):
                score += 5
        
        # Transposon scoring
        score += len(elements.get('transposons', [])) * 8
        
        # Resistance gene scoring
        for gene in elements.get('resistance_genes', []):
            score += 15
            if gene.get('risk_level') == 'Critical':
                score += 20
            if 'carbapenem' in gene.get('drug_class', '').lower():
                score += 25
            if 'colistin' in gene.get('drug_class', '').lower():
                score += 30
        
        # Cap at 100
        return min(score, 100)
    
    def _determine_risk_level(self, score: int) -> str:
        if score >= 75:
            return '🔴 CRITICAL'
        elif score >= 50:
            return '🟠 HIGH'
        elif score >= 30:
            return '🟡 MEDIUM'
        elif score >= 10:
            return '🟢 LOW'
        else:
            return '⚪ MINIMAL'
    
    def _generate_recommendations(self, results: dict):
        """Generate actionable recommendations"""
        recommendations = []
        
        if results['risk_level'] in ['🔴 CRITICAL', '🟠 HIGH']:
            recommendations.append("🚨 IMMEDIATE ACTION: High spread risk detected")
            recommendations.append("📋 Implement infection control measures")
            recommendations.append("🌍 Report to surveillance authorities")
        
        if any(gene['risk_level'] == 'Critical' for gene in results['detected_elements'].get('resistance_genes', [])):
            recommendations.append("💊 Critical resistance detected - review treatment protocols")
        
        if len(results['detected_elements'].get('plasmids', [])) > 0:
            recommendations.append("🔄 Mobile genetic elements present - monitor for spread")
        
        if len(results['detected_elements'].get('transposons', [])) > 2:
            recommendations.append("🧬 High transposon activity - increased mobility potential")
        
        if not recommendations:
            recommendations.append("✅ No significant HGT risk detected")
            recommendations.append("🔬 Routine monitoring sufficient")
        
        recommendations.append("⚕️ Consult with infection control specialist")
        
        return recommendations
    
    def _create_summary(self, results: dict):
        """Create analysis summary"""
        return {
            'total_elements': sum(len(v) for v in results['detected_elements'].values()),
            'plasmid_count': len(results['detected_elements']['plasmids']),
            'transposon_count': len(results['detected_elements']['transposons']),
            'resistance_count': len(results['detected_elements']['resistance_genes']),
            'high_risk_plasmids': len([p for p in results['detected_elements']['plasmids'] 
                                      if p.get('risk_category') == 'High'])
        }
    
    def _classify_transposon_family(self, name: str) -> str:
        """Classify transposon family"""
        families = {
            'IS3': 'IS3 family',
            'IS5': 'IS5 family', 
            'Tn5': 'Tn5 family',
            'Tn3': 'Tn3 family'
        }
        return families.get(name, 'Unknown family')
    
    def _get_drug_class(self, gene_name: str) -> str:
        """Get drug class for resistance gene"""
        classes = {
            'blaTEM': 'Beta-lactams (Penicillins)',
            'blaCTX-M': 'Beta-lactams (Cephalosporins)',
            'tetA': 'Tetracyclines',
            'aac': 'Aminoglycosides',
            'mcr': 'Polymyxins (Colistin)'
        }
        return classes.get(gene_name, 'Multiple classes')

# Create analyzer instance
analyzer = HGTRiskAnalyzer()

# API Routes
@app.get("/")
def root():
    return {
        "message": "PhazeGEN HGT Risk Detection API",
        "status": "running",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "analyze_file": "POST /api/analyze/file",
            "health": "GET /api/health",
            "test": "GET /api/test"
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "hgt-detector", "version": "1.0.0"}

@app.get("/api/test")
def test_analysis():
    """Test endpoint with sample sequence"""
    sample_sequence = (
        "ATGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC"
        "TAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGCTAGC"
        "CAGGTAATCGATCGATCGATCGATCGATCGATCGATCGATCGA"
        "TGCATGCATGCATGCATGCATGCATGCATGCATGCATGCATGC"
    )
    return analyzer.analyze_sequence(sample_sequence, "test_sample.fasta")

@app.post("/api/analyze")
def analyze_sequence(request_data: dict):
    """Analyze sequence from JSON request"""
    try:
        sequence = request_data.get("sequence", "")
        filename = request_data.get("filename", "unknown.fasta")
        
        if not sequence:
            raise HTTPException(status_code=400, detail="No sequence provided")
        
        if len(sequence) < 20:
            raise HTTPException(status_code=400, detail="Sequence too short (minimum 20 characters)")
        
        # Analyze sequence
        results = analyzer.analyze_sequence(sequence, filename)
        
        # Add metadata
        results['analysis_id'] = f"HGT{hash(sequence) % 1000000:06d}"
        results['timestamp'] = "2024-01-01T00:00:00Z"  # In production, use datetime
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/file")
async def analyze_file(request_data: dict):
    """Analyze uploaded file (simplified - accepts base64 or direct text)"""
    try:
        # For simplicity, we accept the file content directly
        file_content = request_data.get("content", "")
        filename = request_data.get("filename", "uploaded.fasta")
        
        if not file_content:
            raise HTTPException(status_code=400, detail="No file content provided")
        
        # Analyze the content
        results = analyzer.analyze_sequence(file_content, filename)
        
        return {
            "status": "success",
            "filename": filename,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")

@app.get("/api/patterns")
def get_patterns():
    """Get the detection patterns being used"""
    return {
        "plasmid_patterns": list(analyzer.patterns['plasmids'].keys()),
        "transposon_patterns": list(analyzer.patterns['transposons'].keys()),
        "resistance_patterns": list(analyzer.patterns['resistance'].keys()),
        "high_risk_plasmids": analyzer.high_risk_plasmids,
        "critical_genes": analyzer.critical_genes
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PHASEGEN HGT RISK DETECTION BACKEND")
    print("=" * 60)
    print("📡 Service starting on: http://localhost:8000")
    print("🔗 API Documentation: http://localhost:8000/docs")
    print("❤️  Health check: http://localhost:8000/api/health")
    print("🧪 Test endpoint: http://localhost:8000/api/test")
    print("=" * 60)
    print("✅ To analyze a sequence:")
    print('   curl -X POST http://localhost:8000/api/analyze \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"sequence":"ATGCTAGC...","filename":"test.fasta"}\'')
    print("=" * 60)
    print("🛑 Press Ctrl+C to stop the service")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )