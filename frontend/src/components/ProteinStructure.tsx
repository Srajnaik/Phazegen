import React from 'react';
import { Box, Layers, Zap } from 'lucide-react';
import type { ProteinStructure as IProteinStructure } from '../services/api';

interface Props {
  data: IProteinStructure;
}

const ProteinStructure: React.FC<Props> = ({ data }) => {
  return (
    <div className="card" style={{ marginTop: '1.5rem', padding: 0, overflow: 'hidden' }}>
      <div style={{ padding: '1rem 1.5rem', background: 'rgba(30, 41, 59, 0.5)', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h3 style={{ fontSize: '1.125rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Box color="var(--primary)" /> Protein Structure Prediction (ESM-Mock)
        </h3>
        <span style={{ fontSize: '0.75rem', background: '#475569', padding: '2px 8px', borderRadius: '4px' }}>In-Silico</span>
      </div>
      
      <div className="grid-2" style={{ padding: '1.5rem' }}>
        {/* Mock Visualizer Placeholder */}
        <div style={{ 
          background: '#020617', borderRadius: '8px', aspectRatio: '16/9', 
          display: 'flex', alignItems: 'center', justifyContent: 'center', 
          position: 'relative', overflow: 'hidden', border: '1px solid var(--border-color)' 
        }}>
          <div style={{ textAlign: 'center', zIndex: 10 }}>
            <Layers size={48} color="var(--primary)" style={{ margin: '0 auto 0.5rem auto', opacity: 0.8 }} />
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>3D Structure Visualization</p>
            <p style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.25rem' }}>ID: {data.structure_id}</p>
          </div>
        </div>

        {/* Data Panel */}
        <div className="flex-col">
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Folding Type</p>
            <p style={{ fontWeight: '500' }}>{data.folding_type}</p>
          </div>
          
          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>pLDDT Confidence</p>
            <div className="flex-row" style={{ gap: '0.5rem' }}>
              <div className="progress-container">
                <div 
                  className="progress-bar" 
                  style={{ width: `${data.confidence_score}%` }}
                ></div>
              </div>
              <span style={{ color: 'var(--success)', fontWeight: 'bold' }}>{data.confidence_score}%</span>
            </div>
          </div>

          <div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Molecular Weight</p>
            <p style={{ fontWeight: '500' }}>{data.molecular_weight}</p>
          </div>

          <div style={{ background: 'rgba(51, 65, 85, 0.3)', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div className="flex-row" style={{ alignItems: 'flex-start' }}>
              <Zap size={16} color="var(--warning)" style={{ marginTop: '4px', flexShrink: 0 }} />
              <p style={{ fontSize: '0.875rem', color: '#cbd5e1', fontStyle: 'italic' }}>"{data.description}"</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProteinStructure;