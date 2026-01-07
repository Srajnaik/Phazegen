import subprocess
import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
import tempfile
import shutil

class HGTRiskAnalyzer:
    def __init__(self):
        self.temp_dir = "/tmp/phazegen_hgt"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize databases
        self.db_paths = {
            'card': '/data/db/card',
            'plasmidfinder': '/data/db/plasmidfinder',
            'vfdb': '/data/db/vfdb',
            'isfinder': '/data/db/isfinder'
        }
    
    def analyze_sequence(self, fasta_content: str, filename: str) -> Dict:
        """Main analysis pipeline"""
        results = {
            'sample_id': filename,
            'risk_score': 0,
            'risk_level': 'Low',
            'detected_elements': {},
            'warnings': []
        }
        
        try:
            # 1. Save sequence to temp file
            seq_file = self._save_temp_fasta(fasta_content, filename)
            
            # 2. Run assembly (if needed)
            assembled = self._assemble_if_needed(seq_file)
            
            # 3. Run all analyses
            results['detected_elements']['plasmids'] = self._detect_plasmids(assembled)
            results['detected_elements']['transposons'] = self._detect_transposons(assembled)
            results['detected_elements']['resistance_genes'] = self._detect_resistance_genes(assembled)
            results['detected_elements']['virulence_factors'] = self._detect_virulence(assembled)
            
            # 4. Calculate risk score
            results['risk_score'] = self._calculate_risk_score(results['detected_elements'])
            results['risk_level'] = self._determine_risk_level(results['risk_score'])
            
            # 5. Generate recommendations
            results['recommendations'] = self._generate_recommendations(results)
            
            # 6. Clean up
            self._cleanup_temp_files()
            
        except Exception as e:
            results['error'] = str(e)
            results['warnings'].append(f"Analysis error: {e}")
            
        return results
    
    def _detect_plasmids(self, fasta_file: str) -> List[Dict]:
        """Detect plasmid replicons"""
        plasmids = []
        
        # Using ABRicate with PlasmidFinder database
        cmd = [
            'abricate', '--db', 'plasmidfinder',
            '--minid', '90', '--mincov', '80',
            fasta_file
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')
            
            for line in lines[1:]:  # Skip header
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 8:
                        plasmid = {
                            'replicon': parts[5],
                            'coverage': float(parts[7]),
                            'identity': float(parts[8]),
                            'accession': parts[1],
                            'position': f"{parts[2]}-{parts[3]}"
                        }
                        
                        # Classify plasmid type
                        plasmid['incompatibility_group'] = self._classify_incompatibility(parts[5])
                        plasmid['risk_category'] = self._plasmid_risk_category(parts[5])
                        
                        plasmids.append(plasmid)
                        
        except subprocess.CalledProcessError as e:
            # Fallback to BLAST if ABRicate fails
            plasmids = self._fallback_plasmid_detection(fasta_file)
            
        return plasmids
    
    def _detect_transposons(self, fasta_file: str) -> List[Dict]:
        """Detect transposons and insertion sequences"""
        transposons = []
        
        # Check for transposase genes
        cmd = [
            'blastn', '-query', fasta_file,
            '-db', self.db_paths['isfinder'],
            '-outfmt', '6',
            '-evalue', '1e-10',
            '-perc_identity', '80'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 12:
                        transposon = {
                            'type': 'Insertion Sequence',
                            'name': parts[1],
                            'position': f"{parts[8]}-{parts[9]}",
                            'evalue': float(parts[10]),
                            'identity': float(parts[2])
                        }
                        
                        # Classify transposon family
                        transposon['family'] = self._classify_transposon_family(parts[1])
                        transposons.append(transposon)
                        
        except Exception as e:
            print(f"Transposon detection error: {e}")
            
        return transposons
    
    def _detect_resistance_genes(self, fasta_file: str) -> List[Dict]:
        """Detect antibiotic resistance genes"""
        resistance_genes = []
        
        # Use RGI (Resistance Gene Identifier)
        cmd = [
            'rgi', 'main',
            '-i', fasta_file,
            '-o', os.path.join(self.temp_dir, 'rgi_output'),
            '-t', 'contig',
            '--clean'
        ]
        
        try:
            subprocess.run(cmd, capture_output=True)
            
            # Parse RGI output
            rgi_file = os.path.join(self.temp_dir, 'rgi_output.txt')
            if os.path.exists(rgi_file):
                with open(rgi_file, 'r') as f:
                    lines = f.readlines()
                    
                for line in lines[1:]:  # Skip header
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 16:
                            gene = {
                                'gene': parts[8],
                                'drug_class': parts[15],
                                'resistance_mechanism': parts[16] if len(parts) > 16 else '',
                                'amr_family': parts[9],
                                'risk_level': self._gene_risk_level(parts[8])
                            }
                            resistance_genes.append(gene)
                            
        except Exception as e:
            # Fallback to ABRicate with CARD
            cmd = ['abricate', '--db', 'card', fasta_file]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Parse ABRicate output similarly
            # ... parsing logic ...
            
        return resistance_genes
    
    def _calculate_risk_score(self, elements: Dict) -> int:
        """Calculate HGT risk score (0-100)"""
        score = 0
        
        # Plasmid scoring
        plasmids = elements.get('plasmids', [])
        for plasmid in plasmids:
            score += 10  # Base plasmid score
            
            # High-risk plasmids
            high_risk_replicons = ['IncF', 'IncI', 'IncA/C', 'IncX', 'IncN']
            if any(hr in plasmid.get('replicon', '') for hr in high_risk_replicons):
                score += 15
                
            # Broad host range
            if plasmid.get('incompatibility_group') in ['IncP', 'IncQ', 'IncW']:
                score += 20
        
        # Transposon scoring
        transposons = elements.get('transposons', [])
        score += len(transposons) * 5
        
        # Resistance gene scoring
        resistance_genes = elements.get('resistance_genes', [])
        for gene in resistance_genes:
            score += 5
            if gene.get('risk_level') == 'High':
                score += 10
            if 'carbapenem' in gene.get('drug_class', '').lower():
                score += 15
            if 'colistin' in gene.get('drug_class', '').lower():
                score += 20
        
        # Virulence factor scoring
        virulence = elements.get('virulence_factors', [])
        score += len(virulence) * 3
        
        # Cap score at 100
        return min(score, 100)
    
    def _determine_risk_level(self, score: int) -> str:
        if score >= 70:
            return 'Critical'
        elif score >= 50:
            return 'High'
        elif score >= 30:
            return 'Medium'
        elif score >= 10:
            return 'Low'
        else:
            return 'Minimal'
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Generate actionable recommendations based on risk"""
        recommendations = []
        
        if results['risk_level'] in ['High', 'Critical']:
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED: High risk of spread detected")
            
            if any('carbapenem' in str(gene).lower() for gene in results['detected_elements'].get('resistance_genes', [])):
                recommendations.append("🔬 Confirm carbapenemase activity with phenotypic testing")
                
            if len(results['detected_elements'].get('plasmids', [])) > 0:
                recommendations.append("📋 Implement contact precautions for affected patients")
                recommendations.append("🌍 Report to regional surveillance system")
                
        elif results['risk_level'] == 'Medium':
            recommendations.append("⚠️ Enhanced surveillance recommended")
            recommendations.append("🔍 Monitor for spread within facility")
            
        elif results['risk_level'] in ['Low', 'Minimal']:
            recommendations.append("✅ Routine monitoring sufficient")
            
        # Specific recommendations
        if any('mcr' in str(gene).lower() for gene in results['detected_elements'].get('resistance_genes', [])):
            recommendations.append("💊 Colistin resistance detected - consider alternative therapies")
            
        if len(results['detected_elements'].get('transposons', [])) > 3:
            recommendations.append("🔄 High transposon activity - increased mobility potential")
            
        return recommendations
    
    # Helper methods
    def _save_temp_fasta(self, content: str, filename: str) -> str:
        """Save FASTA content to temporary file"""
        temp_file = os.path.join(self.temp_dir, f"{filename}_{os.getpid()}.fasta")
        with open(temp_file, 'w') as f:
            f.write(content)
        return temp_file
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        os.makedirs(self.temp_dir, exist_ok=True)