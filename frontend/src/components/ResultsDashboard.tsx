import React from 'react';
import { AlertTriangle, CheckCircle, Dna, ShieldAlert, Thermometer, FlaskConical, Network } from 'lucide-react';
import type { AnalysisResult } from '../services/api';
import ProteinStructure from './ProteinStructure';

interface Props {
  results: AnalysisResult;
}

const ResultsDashboard: React.FC<Props> = ({ results }) => {
  const getRiskStyle = (level: string) => {
    switch (level) {
      case 'High': return { color: 'var(--danger)', borderColor: 'var(--danger)', background: 'var(--danger-bg)' };
      case 'Medium': return { color: 'var(--warning)', borderColor: 'var(--warning)', background: 'var(--warning-bg)' };
      default: return { color: 'var(--success)', borderColor: 'var(--success)', background: 'var(--success-bg)' };
    }
  };

  const riskStyle = getRiskStyle(results.risk_level);

  // Helper to ensure safe access if advanced_ml is missing (backward compatibility)
  const virulence = results.advanced_ml?.virulence || { virulenceScore: 0, factors: [] };
  const hgt = results.advanced_ml?.hgt_risk || { risk: 'Unknown', score: 0 };

  return (
    <div className="flex-col" style={{ gap: '1.5rem' }}>
      {/* Top Metrics Row */}
      <div className="grid-3">
        {/* Risk Score */}
        <div className="card flex-row space-between" style={{ ...riskStyle, borderWidth: '1px', borderStyle: 'solid' }}>
          <div>
            <p style={{ fontSize: '0.875rem', opacity: 0.8 }}>Pathogenic Risk</p>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{results.risk_level}</h2>
          </div>
          <div style={{ 
            height: '48px', width: '48px', borderRadius: '50%', 
            border: '4px solid currentColor', display: 'flex', 
            alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' 
          }}>
            {Math.round(results.risk_score * 100)}
          </div>
        </div>

        {/* CRISPR Status */}
        <div className="card flex-row">
          <div style={{ padding: '10px', borderRadius: '8px', background: results.crispr_status === 'Present' ? 'var(--success-bg)' : '#334155', color: results.crispr_status === 'Present' ? 'var(--success)' : '#94a3b8' }}>
            <ShieldAlert size={24} />
          </div>
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>CRISPR Cas-System</p>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{results.crispr_status}</h2>
          </div>
        </div>

        {/* GC Content */}
        <div className="card flex-row">
          <div style={{ padding: '10px', borderRadius: '8px', background: 'rgba(37, 99, 235, 0.2)', color: 'var(--accent-blue)' }}>
            <Dna size={24} />
          </div>
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>GC Content</p>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>{results.metadata.gc_content.toFixed(1)}%</h2>
          </div>
        </div>
      </div>

      {/* Main Analysis Section */}
      <div className="grid-2">
        {/* Resistance Genes List */}
        <div className="card" style={{ gridColumn: 'span 1' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
            <Thermometer size={20} color="var(--primary)" />
            Detected Resistance Genes
          </h3>
          
          {results.resistance_genes.length === 0 ? (
            <div style={{ padding: '1rem', background: 'var(--success-bg)', color: 'var(--success)', borderRadius: '8px', display: 'flex', gap: '0.5rem' }}>
              <CheckCircle size={20} /> No known resistance markers detected.
            </div>
          ) : (
            <div className="flex-col">
              {results.resistance_genes.map((gene, idx) => (
                <div key={idx} className="flex-row space-between" style={{ padding: '0.75rem', background: 'rgba(0,0,0,0.2)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div>
                    <p style={{ fontWeight: 'bold' }}>{gene.gene}</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{gene.class}</p>
                  </div>
                  <span className="badge badge-red">
                    Conf: {(gene.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              ))}
            </div>
          )}
          
          <div style={{ marginTop: '1.5rem' }}>
            <h4 style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>AI Analysis Summary</h4>
            <p style={{ fontSize: '0.875rem', lineHeight: '1.6', background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px' }}>
              {results.explanation}
            </p>
          </div>
        </div>

        {/* Metadata & Advanced ML */}
        <div className="flex-col" style={{ gap: '1.5rem' }}>
            {/* Standard Metadata */}
            <div className="card">
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem' }}>Genome Metadata</h3>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <li className="flex-row space-between" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>Total Length</span>
                    <span style={{ fontFamily: 'monospace' }}>{results.metadata.length.toLocaleString()} bp</span>
                    </li>
                    <li className="flex-row space-between" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>
                    <span style={{ color: 'var(--text-muted)' }}>ORFs Identified</span>
                    <span style={{ fontFamily: 'monospace' }}>{results.metadata.orf_count}</span>
                    </li>
                </ul>
                <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--warning-bg)', borderRadius: '8px', border: '1px solid rgba(234, 179, 8, 0.2)' }}>
                    <div className="flex-row" style={{ gap: '0.5rem' }}>
                    <AlertTriangle size={18} color="var(--warning)" />
                    <p style={{ fontSize: '0.75rem', color: '#fef3c7' }}>
                        Research prototype. Not for clinical use.
                    </p>
                    </div>
                </div>
            </div>

            {/* NEW: Advanced ML Card */}
            {results.advanced_ml && (
                <div className="card" style={{ background: 'linear-gradient(to bottom right, #1e293b, #0f172a)' }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: '600', marginBottom: '1rem', color: 'var(--primary)' }}>Advanced ML Insights</h3>
                    
                    {/* Virulence Section */}
                    <div style={{ marginBottom: '1rem' }}>
                        <div className="flex-row space-between" style={{ marginBottom: '0.5rem' }}>
                            <div className="flex-row" style={{ gap: '0.5rem' }}>
                                <FlaskConical size={16} color="#e2e8f0" />
                                <span style={{ fontSize: '0.875rem' }}>Virulence Score</span>
                            </div>
                            <span style={{ fontWeight: 'bold' }}>{virulence.virulenceScore}/100</span>
                        </div>
                        <div className="progress-container" style={{ height: '4px', background: '#334155' }}>
                            <div className="progress-bar" style={{ width: `${virulence.virulenceScore}%`, background: '#f43f5e' }}></div>
                        </div>
                    </div>

                    {/* HGT Section */}
                    <div>
                        <div className="flex-row space-between" style={{ marginBottom: '0.5rem' }}>
                             <div className="flex-row" style={{ gap: '0.5rem' }}>
                                <Network size={16} color="#e2e8f0" />
                                <span style={{ fontSize: '0.875rem' }}>HGT Risk (Gene Transfer)</span>
                            </div>
                            <span className={`badge ${hgt.risk === 'High' ? 'badge-red' : hgt.risk === 'Medium' ? 'badge-yellow' : 'badge-green'}`}>
                                {hgt.risk}
                            </span>
                        </div>
                    </div>
                </div>
            )}
        </div>
      </div>

      {/* Protein Structure Module */}
      {results.protein_structure && (
        <ProteinStructure data={results.protein_structure} />
      )}
    </div>
  );
};

export default ResultsDashboard;